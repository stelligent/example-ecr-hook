import logging
from typing import Any, MutableMapping, Optional

from cloudformation_cli_python_lib import (
    BaseHookHandlerRequest,
    HandlerErrorCode,
    Hook,
    HookInvocationPoint,
    OperationStatus,
    ProgressEvent,
    SessionProxy,
    exceptions,
)

from .models import HookHandlerRequest, TypeConfigurationModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
TYPE_NAME = "Stelligent::ECRExample::Hook"

hook = Hook(TYPE_NAME, TypeConfigurationModel)
test_entrypoint = hook.test_entrypoint

def validate_ecr_repo(
        repo_properties
) -> ProgressEvent:
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS
    )

    error_messages = []

    # Check Encryption
    repo_encryption_type = repo_properties.get("EncryptionConfiguration", {}).get("EncryptionType")
    if repo_encryption_type != "KMS":
        error_messages.append("EncryptionType must be KMS")

    # Check Scan on Push
    scan_on_push = repo_properties.get("ImageScanningConfiguration", {}).get("ScanOnPush")
    if scan_on_push != "true":
        error_messages.append("ScanOnPush must be enabled")

    # Check Image Tag Mutability
    image_tag_mutability = repo_properties.get("ImageTagMutability")
    if image_tag_mutability != "IMMUTABLE":
        error_messages.append("ImageTagMutability must be IMMUTABLE")

    if error_messages:
        progress.status = OperationStatus.FAILED
        progress.message = "\n".join(error_messages)
        progress.errorCode = HandlerErrorCode.NonCompliant
    else:
        progress.status = OperationStatus.SUCCESS
        progress.message = "No issues found"
    return progress

@hook.handler(HookInvocationPoint.CREATE_PRE_PROVISION)
def pre_create_handler(
        session: Optional[SessionProxy],
        request: HookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: TypeConfigurationModel
) -> ProgressEvent:
    target_model = request.hookContext.targetModel
    target_name = request.hookContext.targetName

    try:
        # Verify this is a ECR Repo resource
        if "AWS::ECR::Repository" == target_name:
            return validate_ecr_repo(target_model.get("resourceProperties"))
        else:
            raise exceptions.InvalidRequest(f"Unknown target type: {target_name}")
    except TypeError as e:
        raise exceptions.InternalFailure(f"was not expecting type {e}")


@hook.handler(HookInvocationPoint.UPDATE_PRE_PROVISION)
def pre_update_handler(
        session: Optional[SessionProxy],
        request: HookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: TypeConfigurationModel
) -> ProgressEvent:
    target_model = request.hookContext.targetModel
    target_name = request.hookContext.targetName

    try:
        # Verify this is a ECR Repo resource
        if "AWS::ECR::Repository" == target_name:
            # Currently only needs the intended resources, rather than the previous values
            # target_model.get("previousResourceProperties")
            return validate_ecr_repo(target_model.get("resourceProperties"))
        else:
            raise exceptions.InvalidRequest(f"Unknown target type: {target_name}")
    except TypeError as e:
        progress = ProgressEvent.failed(HandlerErrorCode.InternalFailure, f"was not expecting type {e}")

    return progress


@hook.handler(HookInvocationPoint.DELETE_PRE_PROVISION)
def pre_delete_handler(
        session: Optional[SessionProxy],
        request: BaseHookHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_configuration: TypeConfigurationModel
) -> ProgressEvent:
    return ProgressEvent(
        status=OperationStatus.SUCCESS
    )
