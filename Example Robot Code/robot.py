import cv2
import os
import time
from datetime import datetime
import numpy as np

class RobotVisionSystem:
    """
    A robot vision system for capturing and saving images.
    Supports both single captures and continuous monitoring.
    """
    
    def __init__(self, camera_id=0, save_directory="robot_captures"):
        """
        Initialize the vision system.
        
        Args:
            camera_id (int): Camera device ID (0 for default webcam)
            save_directory (str): Directory to save captured images
        """
        self.camera_id = camera_id
        self.save_directory = save_directory
        self.cap = None
        self.is_capturing = False
        
        # Create save directory if it doesn't exist
        os.makedirs(self.save_directory, exist_ok=True)

        print(f"Current working directory: {os.getcwd()}")
        print(f"Full path to images: {os.path.join(os.getcwd(), 'robot_captures')}")
        
    def initialize_camera(self):
        """Initialize the camera connection."""
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            raise Exception(f"Could not open camera {self.camera_id}")
            
        # Set camera properties (optional)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        print(f"Camera {self.camera_id} initialized successfully")
        
    def capture_single_image(self, filename=None):
        """
        Capture a single image and save it.
        
        Args:
            filename (str): Optional custom filename. If None, uses timestamp.
            
        Returns:
            str: Path to saved image file
        """
        if self.cap is None:
            self.initialize_camera()
            
        ret, frame = self.cap.read()
        
        if not ret:
            raise Exception("Failed to capture image from camera")
            
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"robot_capture_{timestamp}.jpg"
            
        # Ensure filename has .jpg extension
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filename += '.jpg'
            
        filepath = os.path.join(self.save_directory, filename)
        
        # Save the image
        success = cv2.imwrite(filepath, frame)
        
        if success:
            print(f"Image saved: {filepath}")
            print(f"Image size: {frame.shape[1]}x{frame.shape[0]} pixels")
            return filepath
        else:
            raise Exception(f"Failed to save image to {filepath}")
    
    def capture_multiple_images(self, count=5, interval=1.0):
        """
        Capture multiple images with specified interval.
        
        Args:
            count (int): Number of images to capture
            interval (float): Time interval between captures in seconds
            
        Returns:
            list: List of saved image file paths
        """
        if self.cap is None:
            self.initialize_camera()
            
        saved_files = []
        
        print(f"Capturing {count} images with {interval}s interval...")
        
        for i in range(count):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
            filename = f"robot_sequence_{i+1:03d}_{timestamp}.jpg"
            
            try:
                filepath = self.capture_single_image(filename)
                saved_files.append(filepath)
                print(f"Captured {i+1}/{count}")
                
                if i < count - 1:  # Don't wait after the last image
                    time.sleep(interval)
                    
            except Exception as e:
                print(f"Error capturing image {i+1}: {e}")
                
        return saved_files
    
    def start_continuous_capture(self, save_interval=5.0, max_images=None):
        """
        Start continuous image capture at regular intervals.
        
        Args:
            save_interval (float): Seconds between automatic saves
            max_images (int): Maximum number of images to capture (None for unlimited)
        """
        if self.cap is None:
            self.initialize_camera()
            
        self.is_capturing = True
        image_count = 0
        
        print(f"Starting continuous capture (interval: {save_interval}s)")
        print("Press 'q' to stop, 's' to save current frame, 'p' to pause/resume")
        
        last_save_time = time.time()
        paused = False
        
        while self.is_capturing:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Failed to read frame")
                break
                
            # Display the frame (optional)
            cv2.imshow('Robot Vision - Press q to quit, s to save, p to pause', frame)
            
            current_time = time.time()
            
            # Auto-save based on interval
            if not paused and (current_time - last_save_time) >= save_interval:
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"robot_auto_{image_count+1:04d}_{timestamp}.jpg"
                    filepath = self.capture_single_image(filename)
                    image_count += 1
                    last_save_time = current_time
                    
                    if max_images and image_count >= max_images:
                        print(f"Reached maximum image count: {max_images}")
                        break
                        
                except Exception as e:
                    print(f"Auto-save failed: {e}")
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Stopping continuous capture...")
                break
            elif key == ord('s'):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"robot_manual_{timestamp}.jpg"
                    self.capture_single_image(filename)
                    print("Manual capture saved")
                except Exception as e:
                    print(f"Manual save failed: {e}")
            elif key == ord('p'):
                paused = not paused
                status = "paused" if paused else "resumed"
                print(f"Capture {status}")
        
        self.is_capturing = False
        cv2.destroyAllWindows()
        print(f"Continuous capture stopped. Total images: {image_count}")
    
    def capture_with_detection(self, detection_threshold=0.3):
        """
        Capture images when motion is detected (simple example).
        
        Args:
            detection_threshold (float): Motion detection sensitivity
        """
        if self.cap is None:
            self.initialize_camera()
            
        print("Starting motion-triggered capture...")
        print("Press 'q' to quit")
        
        # Initialize background subtractor for motion detection
        backSub = cv2.createBackgroundSubtractorMOG2()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Apply background subtraction
            fgMask = backSub.apply(frame)
            
            # Calculate motion percentage
            motion_pixels = cv2.countNonZero(fgMask)
            total_pixels = fgMask.shape[0] * fgMask.shape[1]
            motion_percentage = motion_pixels / total_pixels
            
            # If significant motion detected, save image
            if motion_percentage > detection_threshold:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"robot_motion_{timestamp}.jpg"
                try:
                    self.capture_single_image(filename)
                    print(f"Motion detected! Saved: {filename}")
                except Exception as e:
                    print(f"Failed to save motion capture: {e}")
            
            # Display frame with motion overlay
            cv2.imshow('Motion Detection - Press q to quit', frame)
            cv2.imshow('Motion Mask', fgMask)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Camera resources released")

# Example usage and demonstration
def main():
    """Demonstrate the robot vision system capabilities."""
    
    # Initialize the vision system
    robot_vision = RobotVisionSystem(camera_id=0, save_directory="robot_captures")
    
    try:
        print("=== Robot Vision System Demo ===")
        
        # Example 1: Single image capture
        print("\n1. Capturing single image...")
        robot_vision.capture_single_image("test_single.jpg")
        
        # Example 2: Multiple images with interval
        # print("\n2. Capturing sequence of 3 images...")
        # files = robot_vision.capture_multiple_images(count=3, interval=2.0)
        # print(f"Saved files: {files}")
        
        # Example 3: Continuous capture (uncomment to use)
        # print("\n3. Starting continuous capture...")
        # robot_vision.start_continuous_capture(save_interval=3.0, max_images=5)
        
        # Example 4: Motion-triggered capture (uncomment to use)
        # print("\n4. Starting motion detection capture...")
        # robot_vision.capture_with_detection(detection_threshold=0.1)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        robot_vision.cleanup()

if __name__ == "__main__":
    main()

# Additional utility functions for robot integration
def integrate_with_robot_navigation(robot_vision, waypoints):
    """
    Example function showing how to integrate image capture with robot navigation.
    
    Args:
        robot_vision: RobotVisionSystem instance
        waypoints: List of (x, y) coordinates for robot navigation
    """
    print("Integrating vision with robot navigation...")
    
    for i, waypoint in enumerate(waypoints):
        print(f"Moving to waypoint {i+1}: {waypoint}")
        
        # Simulate robot movement (replace with actual robot control)
        time.sleep(2)
        
        # Capture image at each waypoint
        filename = f"waypoint_{i+1}_x{waypoint[0]}_y{waypoint[1]}.jpg"
        try:
            robot_vision.capture_single_image(filename)
            print(f"Image captured at waypoint {i+1}")
        except Exception as e:
            print(f"Failed to capture at waypoint {i+1}: {e}")

# Example waypoints for navigation integration
example_waypoints = [(0, 0), (10, 5), (20, 10), (15, 15), (0, 0)]

# Uncomment to test navigation integration:
robot_vision = RobotVisionSystem()
# integrate_with_robot_navigation(robot_vision, example_waypoints)