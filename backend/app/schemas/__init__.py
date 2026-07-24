"""
Campus Copies ERP - Schemas Package Root
"""

from app.schemas.audit import AuditLogCreate, AuditLogResponse
from app.schemas.auth import (
    AdminAuthResponse,
    AdminLoginRequest,
    AdminResponse,
    StudentAuthResponse,
    StudentLoginRequest,
    StudentProfileResponse,
    StudentResponse,
    TokenPayload,
)
from app.schemas.file import FileMetadataResponse, FileUploadResponse, SignedUrlResponse
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemOut,
    InventoryItemUpdate,
    InventoryStockAdjustment,
    InventoryTransactionOut,
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)
from app.schemas.order import (
    OrderCreateRequest,
    OrderFileItemResponse,
    OrderResponse,
    OrderStatusHistoryResponse,
    OrderStatusUpdateRequest,
    PaginatedOrdersResponse,
)
from app.schemas.payment import (
    ExpenseCreateRequest,
    ExpenseResponse,
    FinanceBalanceResponse,
    FinanceSummaryResponse,
    LedgerEntryResponse,
    PaginatedExpensesResponse,
    PaginatedLedgerResponse,
    PaymentRefundRequest,
    PaymentResponse,
    PaymentVerifyRequest,
)
from app.schemas.setting import (
    ApplicationSettingCreate,
    ApplicationSettingResponse,
    ApplicationSettingUpdate,
)
from app.schemas.system import SystemBackupResponse, SystemHealthResponse

__all__ = [
    "StudentLoginRequest",
    "StudentResponse",
    "StudentAuthResponse",
    "StudentProfileResponse",
    "AdminLoginRequest",
    "AdminResponse",
    "AdminAuthResponse",
    "TokenPayload",
    "FileUploadResponse",
    "FileMetadataResponse",
    "SignedUrlResponse",
    "OrderCreateRequest",
    "OrderStatusUpdateRequest",
    "OrderFileItemResponse",
    "OrderStatusHistoryResponse",
    "OrderResponse",
    "PaginatedOrdersResponse",
    "PaymentVerifyRequest",
    "PaymentRefundRequest",
    "PaymentResponse",
    "ExpenseCreateRequest",
    "ExpenseResponse",
    "PaginatedExpensesResponse",
    "FinanceBalanceResponse",
    "FinanceSummaryResponse",
    "LedgerEntryResponse",
    "PaginatedLedgerResponse",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItemOut",
    "InventoryTransactionOut",
    "InventoryStockAdjustment",
    "ApplicationSettingCreate",
    "ApplicationSettingUpdate",
    "ApplicationSettingResponse",
    "AuditLogCreate",
    "AuditLogResponse",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "SystemHealthResponse",
    "SystemBackupResponse",
]
