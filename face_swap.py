import cv2, numpy as np

def swap_faces(source_image, destination_image):
    source_img = cv2.imread(source_image)
    destination_img = cv2.imread(destination_image)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    source_faces = face_cascade.detectMultiScale(source_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    destination_faces = face_cascade.detectMultiScale(destination_img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if len(source_faces) == 0 or len(destination_faces) == 0:
        print("No faces detected in one or both images.")
        return None
    
    source_x, source_y, source_w, source_h = source_faces[0]
    destination_x, destination_y, destination_w, destination_h = destination_faces[0]
    source_roi = source_img[source_y:source_y + source_h, source_x:source_x + source_w]
    destination_roi = destination_img[destination_y:destination_y + destination_h, destination_x:destination_x + destination_w]
    # https://github.com/spmallick/learnopencv/blob/master/AgeGender/opencv_face_detector_uint8.pb
    model_path = "path/to/opencv_face_detector_uint8.pb"
    config_path = "path/to/opencv_face_detector.pbtxt"
    net = cv2.dnn.readNetFromTensorflow(model_path, config_path)
    blob = cv2.dnn.blobFromImage(destination_roi, 1.0, (300, 300), [104, 117, 123], False)
    net.setInput(blob)
    landmarks = net.forward()
    
    destination_points = []
    for i in range(68):
        x = int(landmarks[0, 0, i, 0] * destination_w) + destination_x
        y = int(landmarks[0, 0, i, 1] * destination_h) + destination_y
        destination_points.append((x, y))
        
    hull_points = cv2.convexHull(np.array(destination_points), returnPoints=True)
    mask = np.zeros(source_img.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(destination_points)], 255)
    
    transformation_matrix, _ = cv2.estimateAffinePartial2D(np.array(destination_points), np.array(source_faces)[:,:2])
    source_face_warped = cv2.warpAffine(source_roi, transformation_matrix, (destination_w, destination_h))
    
    destination_face_masked = cv2.bitwise_and(destination_roi, destination_roi, mask=mask)
    swapped_face = cv2.add(destination_face_masked, source_face_warped)
    
    destination_img[destination_y:destination_y + destination_h, destination_x:destination_x + destination_w] = swapped_face
    return destination_img