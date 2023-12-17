import datetime

from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowing.models import Borrowing
from notifications.bot_commands import send_payment_notification
from payment.models import Payment

from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)
from user.permissions import IsAdminOrIfAuthenticatedReadOnly


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly, ]

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = Payment.objects.select_related("user", "borrowing")

            if not self.request.user.is_staff:
                queryset = queryset.filter(user=self.request.user)

        if self.action == "retrieve":
            queryset = Payment.objects.select_related("user", "borrowing")

        return queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action == "list":
            serializer_class = PaymentListSerializer
        elif self.action == "retrieve":
            serializer_class = PaymentDetailSerializer

        return serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SuccessPaymentView(APIView):
    def get(self, request, *args, **kwargs):
        borrowing_id = kwargs.get("pk")

        borrowing = Borrowing.objects.filter(id=borrowing_id).first()
        payment = Payment.objects.filter(borrowing_id=borrowing_id).first()

        if payment and borrowing:
            payment.status = "PAID"
            borrowing.actual_return_date = datetime.date.today()
            borrowing.book.inventory -= 1
            borrowing.user = self.request.user
            borrowing.book.save()
            borrowing.save()
            payment.save()

            if borrowing.user.telegram_id and borrowing.user.telegram_notifications_enabled:
                send_payment_notification(borrowing.user.telegram_id, payment)

            return Response(
                {"message": "Payment of the borrowed book was successful."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Payment not found or already completed."},
                status=status.HTTP_400_BAD_REQUEST
            )


class CancelPaymentView(APIView):
    def get(self, request, *args, **kwargs):
        borrowing_id = kwargs.get("pk")
        payment = Payment.objects.filter(borrowing_id=borrowing_id).first()

        if payment:

            return Response(
                {"message": "The payment can be made a little later."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Payment not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
