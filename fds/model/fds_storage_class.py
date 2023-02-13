from enum import Enum

class FDSStorageClass(Enum):
  Standard = "STANDARD"
  StandardInfrequentAccess = "STANDARD_IA"
  Archive = "ARCHIVE"

class FDSRestoreResult(Enum):
  Restore = "RESTORE"
  Restoring = "RESTORING"
  Restored = "RESTORED"
