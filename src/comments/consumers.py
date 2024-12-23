from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.observer import model_observer

from .models import Comment


class CommentConsumer(AsyncAPIConsumer):
    queryset = Comment.objects.all()

    async def connect(self):
        await self.comment_creation_observer.subscribe()
        await super().connect()

    async def disconnect(self, code):
        pass

    @model_observer(Comment)
    async def comment_creation_observer(self, message, action, message_type, observer=None, **kwargs):
        if action == 'create':
            await self.send_json({'uuid': str(message['pk'])})
