import datetime

from drf_spectacular.utils import extend_schema
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
    permission_classes = [
        IsAdminOrIfAuthenticatedReadOnly,
    ]

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

    @extend_schema(
        description="Get all payments is unreal. " "Try get payment by id",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Get one payment from all by id (For admin)",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class SuccessPaymentView(APIView):
    @extend_schema(
        description="Confirm payment by id (For admin)",
    )
    def get(self, request, *args, **kwargs):
        borrowing_id = kwargs.get("pk")

        borrowing = Borrowing.objects.filter(id=borrowing_id).first()
        payment = Payment.objects.filter(borrowing_id=borrowing_id).first()

        if payment and borrowing:
            payment.status = "PAID"
            if borrowing.payments.count() == 2:
                borrowing.actual_return_date = datetime.date.today()
            if borrowing.payments.count() == 1:
                borrowing.book.inventory -= 1
            borrowing.user = self.request.user
            borrowing.book.save()
            borrowing.save()
            payment.save()

            send_payment_notification(borrowing.user, payment)

            return Response(
                {"message": "Payment of the borrowed book was successful."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Payment not found or already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CancelPaymentView(APIView):
    @extend_schema(
        description="Cancel payment by id (For admin)",
    )
    def get(self, request, *args, **kwargs):
        borrowing_id = kwargs.get("pk")
        payment = Payment.objects.filter(borrowing_id=borrowing_id).first()

        if payment:
            return Response(
                {"message": "The payment can be made a little later."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Payment not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
