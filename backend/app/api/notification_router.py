import asyncio
import uuid
import inject
from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
from app.api.decorators import require_authentication
from app.application.services.notification_service import INotificationService
from app.domain.models.schemma import NotificationResponse

router = APIRouter()


@router.websocket("/notifications/ws")
async def websocket_notifications(websocket: WebSocket, request: Request):
    try:
        print("connect websocket...")
        await require_authentication(request)
        print("connect websocket...")
        current_user = request.state.current_user
    except HTTPException:
        await websocket.close(code=1008)
        return

    notification_service: INotificationService = inject.instance(INotificationService)
    
    print("websocket accepted...")
    await websocket.accept()
    print("websocket accepted!!!")
    
    try:
        while True:
            notifications = await notification_service.get_notifications(current_user.id)
            
            await websocket.send_json(notifications.json())
            
            await asyncio.sleep(5) 
    
    except WebSocketDisconnect:
        print("WebSocket desconectado")

@router.get("/notifications", response_model=list[NotificationResponse])
@require_authentication
async def get_notifications(request: Request):
    notification_service: INotificationService = inject.instance(INotificationService)
    current_user = request.state.current_user
    notifications = await notification_service.get_notifications(current_user.id)
    return notifications


@router.post("/notifications/mark_as_read")
@require_authentication
async def mark_as_read(notification_ids: list[uuid.UUID], request: Request):
    notification_service: INotificationService = inject.instance(INotificationService)
    await notification_service.mark_as_read(notification_ids)
    return {"detail": "Notifications marked as read successfully"}
