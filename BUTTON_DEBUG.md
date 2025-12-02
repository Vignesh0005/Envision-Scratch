# Button Debugging Steps

## Current Button Locations:

1. **In ImageList.jsx header** (Image Gallery section):
   - Right side of "Image Gallery" header
   - Blue button with "Collapse Gallery" text
   - Only visible when gallery is expanded

2. **In App.jsx resize handle bar** (above gallery):
   - Blue bar above Image Gallery
   - Button on left side with "Collapse Gallery" text
   - Always visible

## To Verify:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Type: `document.querySelectorAll('button')`
4. Look for buttons with "Collapse" or "Expand" text

## If button still not visible:

Check if ImageList component is rendering:
- In Console: `document.querySelector('[class*="Image Gallery"]')`
- Should return the header element

