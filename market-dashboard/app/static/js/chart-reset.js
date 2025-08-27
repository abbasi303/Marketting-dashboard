// Clear and reset canvas to prevent memory leaks and rendering issues
function resetCanvas(canvasId) {
    const canvas = document.getElementById(canvasId);
    const parent = canvas.parentElement;
    
    // Store original attributes and styles
    const originalHeight = canvas.getAttribute('height');
    const originalWidth = canvas.getAttribute('width');
    const originalStyle = canvas.getAttribute('style');
    
    // Create a replacement canvas with identical properties
    const newCanvas = document.createElement('canvas');
    newCanvas.id = canvasId;
    newCanvas.className = 'chart-canvas';
    
    // Preserve all original attributes
    if (originalHeight) newCanvas.setAttribute('height', originalHeight);
    if (originalWidth) newCanvas.setAttribute('width', originalWidth);
    if (originalStyle) newCanvas.setAttribute('style', originalStyle);
    
    // Explicitly set dimensions
    newCanvas.height = 300;
    newCanvas.width = parent.clientWidth;
    
    console.log(`Resetting canvas ${canvasId} with dimensions: ${newCanvas.width}x${newCanvas.height}`);
    
    // Remove the old canvas and replace with the new one
    parent.removeChild(canvas);
    parent.appendChild(newCanvas);
    
    // Force the canvas to respect container bounds
    newCanvas.style.maxHeight = '100%';
    newCanvas.style.maxWidth = '100%';
    
    return newCanvas.getContext('2d');
}
