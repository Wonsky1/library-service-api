from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentListSerializer, PaymentDetailSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related("borrowing", "user")
    serializer_class = PaymentSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.select_related("borrowing", "user")

        if self.request.user.is_staff:
            return queryset.all()

        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
