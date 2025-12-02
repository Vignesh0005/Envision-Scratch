import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Toolbar from './components/Toolbar'
import ControlBox from './components/ControlBox'
import Display from './components/Display'
import ImageList from './components/ImageList'
import NodularityAnalysis from './components/NodularityAnalysis'
import PhaseSegmentation from './components/PhaseSegmentation'
import InclusionAnalysis from './components/InclusionAnalysis'
import PorosityAnalysis from './components/PorosityAnalysis'
import ShapeTracker from './components/ShapeTracker'

const SIDEBAR_WIDTH = '320px';
const VIEWER_MAX_WIDTH = 'calc(100vw - 340px)';
const VIEWER_MAX_HEIGHT = 'calc(100vh - 120px - 300px)'; // minus top bars and gallery height

const App = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [imagePath, setImagePath] = useState(null);
  const [currentImageUrl, setCurrentImageUrl] = useState(null);
  const [selectedTool, setSelectedTool] = useState('pointer');
  const [measurementData, setMeasurementData] = useState(null);
  const [shapes, setShapes] = useState([]);
  const [selectedShape, setSelectedShape] = useState(null);
  const [currentFolderPath, setCurrentFolderPath] = useState('C:\\Users\\Public\\MicroScope_Images');
  const [currentColor, setCurrentColor] = useState('#00ff00');
  const [currentFontColor, setCurrentFontColor] = useState('#ffffff');
  const [currentThickness, setCurrentThickness] = useState(2);
  const [currentCalibration, setCurrentCalibration] = useState(null);
  const [showNodularity, setShowNodularity] = useState(false);
  const [showPhaseSegmentation, setShowPhaseSegmentation] = useState(false);
  const [showInclusion, setShowInclusion] = useState(false);
  const [showPorosity, setShowPorosity] = useState(false);
  
  // Add state for resizable image gallery
  const [galleryHeight, setGalleryHeight] = useState(300);
  const [isResizing, setIsResizing] = useState(false);
  const [dateFilter, setDateFilter] = useState({ fromDate: '', toDate: '' });

  useEffect(() => {
    const loadCalibration = () => {
      const savedCalibration = localStorage.getItem('currentCalibration');
      if (savedCalibration) {
        setCurrentCalibration(JSON.parse(savedCalibration));
      }
    };
    loadCalibration();
    window.addEventListener('storage', loadCalibration);
    return () => window.removeEventListener('storage', loadCalibration);
  }, []);

  const handleImageLoad = (url) => setCurrentImageUrl(url);
  const handleSelectTool = (toolId) => setSelectedTool(toolId);
  const handleMeasurement = (data) => setMeasurementData(data);
  const handleShapesUpdate = (newShapes) => setShapes(newShapes);
  const handleShapeSelect = (shape) => setSelectedShape(shape);
  const handleClearShapes = () => {
    if (window.confirm('Are you sure you want to clear all measurements and the uploaded image?')) {
      setShapes([]);
      setImagePath(null); // Clear the uploaded image
    }
  };
  const handleImageSelect = (imagePath) => setImagePath(imagePath);
  
  // Add resize handler functions
  const handleResizeStart = (e) => {
    e.preventDefault();
    setIsResizing(true);
  };
  
  // Add global mouse event listeners for resize
  useEffect(() => {
    if (isResizing) {
      const handleMouseMove = (e) => {
        const container = document.querySelector('.main-content-container');
        if (container) {
          const rect = container.getBoundingClientRect();
          const newHeight = rect.bottom - e.clientY;
          const constrainedHeight = Math.max(150, Math.min(600, newHeight));
          setGalleryHeight(constrainedHeight);
        }
      };
      
      const handleMouseUp = () => {
        setIsResizing(false);
      };
      
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing]);
  
  // Add keyboard shortcuts for quick resize
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'ArrowUp':
            e.preventDefault();
            setGalleryHeight(prev => Math.max(150, prev - 50));
            break;
          case 'ArrowDown':
            e.preventDefault();
            setGalleryHeight(prev => Math.min(600, prev + 50));
            break;
          case '0':
            e.preventDefault();
            setGalleryHeight(300); // Reset to default
            break;
        }
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      {/* Top Menu Bars */}
      <div className="flex flex-col w-full z-50">
        <Navbar imagePath={imagePath} setImagePath={setImagePath} />
        {!(showNodularity || showPhaseSegmentation || showInclusion || showPorosity) && (
          <Toolbar 
            onSelectTool={handleSelectTool}
            selectedTool={selectedTool}
            measurementData={measurementData}
            onClearShapes={handleClearShapes}
            onColorChange={setCurrentColor}
            onFontColorChange={setCurrentFontColor}
            onThicknessChange={setCurrentThickness}
            currentColor={currentColor}
            currentFontColor={currentFontColor}
            currentThickness={currentThickness}
            currentCalibration={currentCalibration}
          />
        )}
      </div>
      {/* Main Content Area */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Left Sidebar */}
        <div className="flex flex-col h-full" style={{ width: SIDEBAR_WIDTH, minWidth: SIDEBAR_WIDTH }}>
          {/* Drawn Shapes Panel - fill available space */}
          <div className="flex-1 min-h-0 w-full">
            <ShapeTracker
              shapes={shapes}
              selectedShape={selectedShape}
              onShapeSelect={handleShapeSelect}
              onColorChange={setCurrentColor}
              currentColor={currentColor}
              currentFontColor={currentFontColor}
              onFontColorChange={setCurrentFontColor}
              onShapesUpdate={handleShapesUpdate}
            />
          </div>
          {/* ControlBox at the bottom of the sidebar */}
          <div className="w-full">
            <ControlBox
              isRecording={isRecording}
              setIsRecording={setIsRecording}
              setImagePath={setImagePath}
              onFolderChange={setCurrentFolderPath}
              onDateFilterChange={setDateFilter}
            />
          </div>
        </div>
        {/* Main Image Viewer Centered */}
        <div className="flex-1 flex flex-col overflow-hidden h-full main-content-container">
          {/* Main Display Area */}
          <div 
            className="flex items-center justify-center overflow-hidden transition-all duration-200 ease-out select-none"
            style={{ height: `calc(100% - ${galleryHeight}px)` }}
          >
            <div className="relative bg-white flex items-center justify-center w-full h-full">
              <Display
                isRecording={isRecording}
                imagePath={imagePath}
                onImageLoad={handleImageLoad}
                selectedTool={selectedTool}
                shapes={shapes}
                onShapesUpdate={handleShapesUpdate}
                currentColor={currentColor}
                currentFontColor={currentFontColor}
                currentThickness={currentThickness}
                onColorChange={setCurrentColor}
                onFontColorChange={setCurrentFontColor}
              />
            </div>
          </div>
          
          {/* Resize Handle */}
          <div 
            className="w-full h-2 bg-gradient-to-r from-gray-200 to-gray-300 hover:from-blue-200 hover:to-blue-300 cursor-ns-resize transition-all duration-200 flex items-center justify-center group relative"
            onMouseDown={handleResizeStart}
            style={{ 
              cursor: isResizing ? 'ns-resize' : 'ns-resize',
              background: isResizing ? 'linear-gradient(to right, #93c5fd, #3b82f6)' : undefined
            }}
            title="Drag to resize image gallery • Ctrl+↑/↓ to adjust • Ctrl+0 to reset"
          >
            {/* Visual indicator dots */}
            <div className="flex space-x-1">
              <div className="w-1 h-1 bg-gray-500 rounded-full group-hover:bg-blue-600 transition-colors"></div>
              <div className="w-1 h-1 bg-gray-500 rounded-full group-hover:bg-blue-600 transition-colors"></div>
              <div className="w-1 h-1 bg-gray-500 rounded-full group-hover:bg-blue-600 transition-colors"></div>
            </div>
            
            {/* Resize indicator text */}
            {isResizing && (
              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium shadow-lg z-20">
                {galleryHeight}px
              </div>
            )}
            
            {/* Quick reset button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                setGalleryHeight(300);
              }}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-gray-400 hover:bg-gray-600 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200"
              title="Reset to default size (300px)"
            >
              Reset
            </button>
          </div>
          
          {/* Image Gallery with dynamic height */}
          <div 
            className="w-full border-t border-gray-200 bg-white overflow-hidden transition-all duration-200 ease-out"
            style={{ height: `${galleryHeight}px` }}
          >
            <ImageList
              currentPath={currentFolderPath}
              onSelectImage={handleImageSelect}
              dateFilter={dateFilter}
            />
          </div>
        </div>
      </div>
      {/* Analysis Modals */}
      {showNodularity && (
        <NodularityAnalysis
          onClose={() => setShowNodularity(false)}
          imagePath={imagePath}
          imageUrl={`http://localhost:5000/api/get-image?path=${encodeURIComponent(imagePath)}`}
        />
      )}
      {showPhaseSegmentation && (
        <PhaseSegmentation
          onClose={() => setShowPhaseSegmentation(false)}
          imagePath={imagePath}
          imageUrl={`http://localhost:5000/api/get-image?path=${encodeURIComponent(imagePath)}`}
        />
      )}
      {showInclusion && (
        <InclusionAnalysis
          onClose={() => setShowInclusion(false)}
          imagePath={imagePath}
          imageUrl={`http://localhost:5000/api/get-image?path=${encodeURIComponent(imagePath)}`}
        />
      )}
      {showPorosity && (
        <PorosityAnalysis
          onClose={() => setShowPorosity(false)}
          imagePath={imagePath}
          imageUrl={`http://localhost:5000/api/get-image?path=${encodeURIComponent(imagePath)}`}
        />
      )}
    </div>
  );
};

export default App;