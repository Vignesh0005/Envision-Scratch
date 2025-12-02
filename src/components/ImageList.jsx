import React, { useState, useEffect } from 'react';

const ImageList = ({ currentPath, onSelectImage, dateFilter }) => {
  const [images, setImages] = useState([]);
  const [allImages, setAllImages] = useState([]); // Store all images before filtering
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false); // Gallery starts collapsed

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
    if (!dateFilter || (!dateFilter.fromDate && !dateFilter.toDate)) {
      // No filter applied, show all images
      setImages(allImages);
      return;
    }

    const filtered = allImages.filter(img => {
      if (!img.date) return false;
      
      // Parse image date - handle both Date objects and date strings
      let imageDate = img.date;
      if (typeof imageDate === 'string') {
        imageDate = new Date(imageDate);
      } else if (!(imageDate instanceof Date)) {
        imageDate = new Date(imageDate);
      }
      
      // Check if date is valid
      if (isNaN(imageDate.getTime())) {
        console.warn('Invalid date for image:', img.name, img.date);
        return false;
      }
      
      // Reset time to start of day for comparison
      const imgDateOnly = new Date(imageDate);
      imgDateOnly.setHours(0, 0, 0, 0);

      if (dateFilter.fromDate && dateFilter.toDate) {
        // Both dates provided - range filter
        const from = new Date(dateFilter.fromDate);
        const to = new Date(dateFilter.toDate);
        from.setHours(0, 0, 0, 0);
        to.setHours(23, 59, 59, 999); // End of day
        
        return imgDateOnly >= from && imgDateOnly <= to;
      } else if (dateFilter.fromDate) {
        // Only from date - show images from this date onwards
        const from = new Date(dateFilter.fromDate);
        from.setHours(0, 0, 0, 0);
        return imgDateOnly >= from;
      } else if (dateFilter.toDate) {
        // Only to date - show images up to this date
        const to = new Date(dateFilter.toDate);
        to.setHours(23, 59, 59, 999);
        return imgDateOnly <= to;
      }

      return true; // No filter, show all
    });

    console.log('Date filter applied:', {
      filter: dateFilter,
      totalImages: allImages.length,
      filteredCount: filtered.length
    });
    setImages(filtered);
  }, [dateFilter, allImages]);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="w-full h-full flex flex-col bg-white relative">
      {/* Toggle Button - Always Visible on Top Layer */}
      <div className="w-full bg-gray-100 border-b-2 border-gray-300 shadow-sm relative z-50 flex-shrink-0">
        <button
          onClick={toggleExpand}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-200 active:bg-gray-300 transition-colors cursor-pointer relative z-50"
          aria-expanded={isExpanded}
          aria-controls="panel-content"
          type="button"
          style={{ zIndex: 1000 }}
        >
          <span className="text-sm font-semibold text-gray-800 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Image Gallery {images.length > 0 && `(${images.length})`}
          </span>
          <span 
            className="text-gray-700 text-xl font-bold transition-transform duration-300 select-none"
            style={{ 
              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
              display: 'inline-block',
              lineHeight: '1',
              userSelect: 'none'
            }}
          >
            ▲
          </span>
        </button>
      </div>

      {/* Collapsible Content */}
      <div 
        id="panel-content"
        className={`flex-1 overflow-hidden transition-all duration-300 ease-out ${isExpanded ? '' : 'hidden'}`}
        style={{
          display: isExpanded ? 'flex' : 'none',
          flexDirection: 'column',
          position: 'relative',
          zIndex: 1
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