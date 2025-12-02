import React, { useState, useEffect } from 'react';

const ImageList = ({ currentPath, onSelectImage, dateFilter }) => {
  const [images, setImages] = useState([]);
  const [allImages, setAllImages] = useState([]); // Store all images before filtering
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isExpanded, setIsExpanded] = useState(true); // Gallery starts expanded

  // Add polling interval state (default 5 seconds)
  const POLL_INTERVAL = 5000;

  // Memoize loadImages to prevent unnecessary recreations
  const loadImages = async () => {
    if (!currentPath) return;
    
    try {
      const response = await fetch('http://localhost:5000/api/list-images', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          path: currentPath,
          filters: {
            extensions: ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
          }
        })
      });

      const data = await response.json();
      if (data.status === 'success' && Array.isArray(data.images)) {
        // Map images with proper date objects
        const newImages = data.images.map(img => ({
          ...img,
          path: img.path,
          name: img.name,
          date: new Date(img.date),
          size: img.size,
          thumbnail: `http://localhost:5000/api/thumbnail?path=${encodeURIComponent(img.path)}`
        }));

        // Store all images (filtering will be handled by useEffect)
        setAllImages(newImages);
      }
    } catch (error) {
      console.error('Error loading images:', error);
    } finally {
      setLoading(false);
    }
  };

  // Initial load and path change handler
  useEffect(() => {
    if (currentPath) {
      setLoading(true);
      loadImages();
    }
  }, [currentPath]);

  // Set up polling for updates
  useEffect(() => {
    if (!currentPath) return;

    // Initial load
    loadImages();

    // Set up polling interval
    const intervalId = setInterval(loadImages, POLL_INTERVAL);

    // Cleanup on unmount or path change
    return () => {
      clearInterval(intervalId);
    };
  }, [currentPath, loadImages]);

  // Add folder watch setup
  useEffect(() => {
    const setupFolderWatch = async () => {
      if (!currentPath) return;

      try {
        // Set up folder watch on the backend
        const response = await fetch('http://localhost:5000/api/watch-folder', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ path: currentPath })
        });

        if (!response.ok) {
          console.error('Failed to set up folder watch');
        }
      } catch (error) {
        console.error('Error setting up folder watch:', error);
      }
    };

    setupFolderWatch();
  }, [currentPath]);

  const handleImageClick = (image) => {
    setSelectedImage(image.path);
    if (onSelectImage) {
      onSelectImage(image.path);
    }
  };

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  // Add a helper function to get filename without extension
  const getFileNameWithoutExtension = (filename) => {
    return filename.replace(/\.[^/.]+$/, '');
  };

  // Apply date filter whenever dateFilter or allImages change
  useEffect(() => {
    const filter = dateFilter || { fromDate: '', toDate: '' };
    
    if (!filter.fromDate && !filter.toDate) {
      // No filter applied, show all images
      setImages(allImages);
      return;
    }

    const filtered = allImages.filter(img => {
      const imageDate = new Date(img.date);
      imageDate.setHours(0, 0, 0, 0); // Reset time to start of day for comparison

      if (filter.fromDate && filter.toDate) {
        // Both dates provided - range filter
        const from = new Date(filter.fromDate);
        const to = new Date(filter.toDate);
        from.setHours(0, 0, 0, 0);
        to.setHours(23, 59, 59, 999); // End of day
        return imageDate >= from && imageDate <= to;
      } else if (filter.fromDate) {
        // Only from date - show images from this date onwards
        const from = new Date(filter.fromDate);
        from.setHours(0, 0, 0, 0);
        return imageDate >= from;
      } else if (filter.toDate) {
        // Only to date - show images up to this date
        const to = new Date(filter.toDate);
        to.setHours(23, 59, 59, 999);
        return imageDate <= to;
      }

      return true; // No filter, show all
    });

    setImages(filtered);
  }, [dateFilter, allImages]);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Toggle Button */}
      <button
        className={`toggle-btn w-full bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 border-b border-gray-300 cursor-pointer flex items-center justify-between transition-colors ${isExpanded ? 'active' : ''}`}
        onClick={toggleExpand}
        aria-expanded={isExpanded}
        aria-controls="panel-content"
        style={{
          fontSize: '14px',
          fontWeight: 'medium'
        }}
      >
        <span className="text-sm font-medium">Image Gallery</span>
        <span 
          style={{ 
            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s ease',
            display: 'inline-block',
            fontSize: '12px'
          }}
        >
          ▼
        </span>
      </button>

      {/* Collapsible Content */}
      <div 
        id="panel-content"
        className={`panel-content flex-1 overflow-hidden transition-all duration-300 ease-out ${isExpanded ? 'expanded' : ''}`}
        style={{
          maxHeight: isExpanded ? '100%' : '0',
          overflow: isExpanded ? 'auto' : 'hidden'
        }}
      >
        <div className="h-full">
          <div className="overflow-x-auto overflow-y-auto h-full">
            <div className="flex gap-4 p-4 min-w-max">
              {loading ? (
                <div className="flex items-center justify-center p-4 w-full">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"></div>
                </div>
              ) : images.length === 0 ? (
                <div className="text-center py-4 text-gray-500 w-full">
                  No images found in this folder
                </div>
              ) : (
                images.map((image) => (
                  <div
                    key={image.path}
                    onClick={() => handleImageClick(image)}
                    className={`flex flex-col items-center p-2 rounded-lg cursor-pointer 
                      transition-all duration-200
                      ${selectedImage === image.path 
                        ? 'bg-blue-50 border-blue-300 shadow-sm' 
                        : 'hover:bg-gray-50 border-gray-200'}
                      border w-[200px] flex-shrink-0`}
                  >
                    <div className="relative w-[160px] h-[160px] mb-2">
                      <img
                        src={image.thumbnail}
                        alt={getFileNameWithoutExtension(image.name)}
                        className="w-full h-full object-cover rounded"
                        loading="lazy"
                      />
                    </div>
                    <p className="text-xs text-gray-900 break-words w-full text-center px-1">
                      {getFileNameWithoutExtension(image.name)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageList;