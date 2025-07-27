from linebot.models import (
    TextSendMessage, StickerSendMessage, ImageSendMessage, VideoSendMessage,
    AudioSendMessage, LocationSendMessage, TemplateSendMessage,
    ButtonsTemplate, ConfirmTemplate, CarouselTemplate, ImageCarouselTemplate,
    FlexSendMessage, QuickReply, QuickReplyButton,
    MessageAction, PostbackAction, URIAction, LocationAction
)
from typing import Dict, Any, List, Optional
import json

class LineMessageBuilder:
    """Builder class สำหรับสร้าง LINE Messages จาก template content"""
    
    @staticmethod
    def build_message(message_type: str, content: Dict[str, Any]):
        """สร้าง LINE Message object จาก content"""
        try:
            if message_type == "text":
                return LineMessageBuilder._build_text_message(content)
            elif message_type == "text_v2":
                return LineMessageBuilder._build_text_v2_message(content)
            elif message_type == "sticker":
                return LineMessageBuilder._build_sticker_message(content)
            elif message_type == "image":
                return LineMessageBuilder._build_image_message(content)
            elif message_type == "video":
                return LineMessageBuilder._build_video_message(content)
            elif message_type == "audio":
                return LineMessageBuilder._build_audio_message(content)
            elif message_type == "location":
                return LineMessageBuilder._build_location_message(content)
            elif message_type == "template":
                return LineMessageBuilder._build_template_message(content)
            elif message_type == "flex":
                return LineMessageBuilder._build_flex_message(content)
            else:
                raise ValueError(f"Unsupported message type: {message_type}")
        except Exception as e:
            print(f"Error building message: {e}")
            # Fallback to simple text message
            return TextSendMessage(text=f"Error: {str(e)}")
    
    @staticmethod
    def _build_text_message(content: Dict[str, Any]) -> TextSendMessage:
        """สร้าง Text Message"""
        text = content.get("text", "")
        quick_reply = LineMessageBuilder._build_quick_reply(content.get("quick_reply"))
        return TextSendMessage(text=text, quick_reply=quick_reply)
    
    @staticmethod
    def _build_sticker_message(content: Dict[str, Any]) -> StickerSendMessage:
        """สร้าง Sticker Message"""
        package_id = content.get("package_id", "1")
        sticker_id = content.get("sticker_id", "1")
        quick_reply = LineMessageBuilder._build_quick_reply(content.get("quick_reply"))
        return StickerSendMessage(package_id=package_id, sticker_id=sticker_id, quick_reply=quick_reply)

    @staticmethod
    def _build_image_message(content: Dict[str, Any]) -> ImageSendMessage:
        """สร้าง Image Message"""
        original_content_url = content.get("original_content_url", "")
        preview_image_url = content.get("preview_image_url", original_content_url)
        quick_reply = LineMessageBuilder._build_quick_reply(content.get("quick_reply"))
        return ImageSendMessage(
            original_content_url=original_content_url,
            preview_image_url=preview_image_url,
            quick_reply=quick_reply
        )
    
    @staticmethod
    def _build_video_message(content: Dict[str, Any]) -> VideoSendMessage:
        """สร้าง Video Message"""
        original_content_url = content.get("original_content_url", "")
        preview_image_url = content.get("preview_image_url", "")
        quick_reply = LineMessageBuilder._build_quick_reply(content.get("quick_reply"))
        return VideoSendMessage(
            original_content_url=original_content_url,
            preview_image_url=preview_image_url,
            quick_reply=quick_reply
        )
    
    @staticmethod
    def _build_audio_message(content: Dict[str, Any]) -> AudioSendMessage:
        """สร้าง Audio Message"""
        original_content_url = content.get("original_content_url", "")
        duration = content.get("duration", 1000)
        quick_reply = LineMessageBuilder._build_quick_reply(content.get("quick_reply"))
        return AudioSendMessage(
            original_content_url=original_content_url,
            duration=duration,
            quick_reply=quick_reply
        )
    
    @staticmethod
    def _build_location_message(content: Dict[str, Any]) -> LocationSendMessage:
        """สร้าง Location Message"""
        title = content.get("title", "Location")
        address = content.get("address", "")
        latitude = content.get("latitude", 0.0)
        longitude = content.get("longitude", 0.0)
        quick_reply = LineMessageBuilder._build_quick_reply(content.get("quick_reply"))
        return LocationSendMessage(
            title=title,
            address=address,
            latitude=latitude,
            longitude=longitude,
            quick_reply=quick_reply
        )
    
    @staticmethod
    def _build_quick_reply(quick_reply_data: Optional[Dict[str, Any]]) -> Optional[QuickReply]:
        """สร้าง Quick Reply"""
        if not quick_reply_data or not quick_reply_data.get("items"):
            return None
        
        items = []
        for item in quick_reply_data.get("items", []):
            action_type = item.get("action", {}).get("type", "message")
            if action_type == "message":
                action = MessageAction(
                    label=item.get("action", {}).get("label", ""),
                    text=item.get("action", {}).get("text", "")
                )
            # Add more action types as needed
            else:
                continue
                
            items.append(QuickReplyButton(action=action))
        
        return QuickReply(items=items)
