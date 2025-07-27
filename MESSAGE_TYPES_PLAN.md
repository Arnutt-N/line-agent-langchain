# 📨 LINE Message Types System - แผนการพัฒนา

## 🎯 เป้าหมาย
สร้างระบบจัดเก็บและจัดการ LINE Message Templates เพื่อให้บอทสามารถตอบกลับได้หลากหลายรูปแบบ

## 📝 LINE Message Types ที่รองรับ

### 1. **Text Message**
- ข้อความธรรมดา
- รองรับ Unicode emojis
- Character limit: 5,000

### 2. **Text Message (v2) - Rich Content**
- รองรับ mentions (@user)
- รองรับ LINE emojis
- Formatting: bold, italic, underline

### 3. **Sticker Message**
- LINE Official Stickers
- Custom Stickers (แพ็คสติกเกอร์)
- Package ID + Sticker ID

### 4. **Image Message**
- Original image URL
- Preview image URL
- รองรับ JPEG, PNG

### 5. **Video Message**
- Original video URL
- Preview image URL
- รองรับ MP4

### 6. **Audio Message**
- Original audio URL
- Duration (milliseconds)
- รองรับ M4A, MP3

### 7. **Location Message**
- Title, Address
- Latitude, Longitude
- Google Maps integration

### 8. **Imagemap Message**
- Interactive image with clickable areas
- Multiple action areas
- Custom layouts

### 9. **Template Messages**
- **Buttons Template**: ปุ่มต่าง ๆ
- **Confirm Template**: Yes/No confirmation
- **Carousel Template**: หลายการ์ดเลื่อน
- **Image Carousel**: รูปภาพหลายใบ

### 10. **Flex Message**
- Custom JSON layouts
- Flexible design
- Rich interactive content

### 11. **Carousel Flex Message**
- Multiple Flex Message bubbles
- Horizontal scrolling
- Complex layouts

### 12. **Quick Reply**
- Quick action buttons
- Attached to any message type
- Maximum 13 items

## 🗃️ Database Schema Plan

### Tables:
1. **message_templates** - เก็บ template หลัก
2. **template_content** - เก็บเนื้อหาของแต่ละ type
3. **template_categories** - หมวดหมู่ template
4. **template_usage_log** - สถิติการใช้งาน

## 🎮 Features ที่จะมี

### Admin Panel:
- สร้าง/แก้ไข/ลบ templates
- Preview templates
- Category management
- Usage statistics

### Bot Integration:
- Smart template selection
- Context-aware responses
- A/B testing
- Fallback mechanisms

## 🔧 Implementation Phases

### Phase 1: Foundation
- Database schema
- Basic CRUD operations
- Text & Sticker messages

### Phase 2: Rich Content
- Image, Video, Audio
- Location messages
- Template messages

### Phase 3: Advanced
- Flex Messages
- Carousel Flex
- Smart selection AI

### Phase 4: Management
- Admin UI
- Analytics
- Export/Import

---
**Next:** สร้าง Database Schema และ Models
