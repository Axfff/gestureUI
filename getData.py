import cv2
import mediapipe as mp
import preprocessing

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


# For webcam input:
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
with mp_hands.Hands(
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # undistort
        mtx, dist = preprocessing.getCameraProperties()
        image = preprocessing.imgCorrection(image, mtx, dist)

        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            print(results)
            for hand_landmarks in results.multi_hand_landmarks:

                coors = []
                # print(hand_landmarks)
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    coors.append((landmark.x, landmark.y, landmark.z))
                coors = preprocessing.coordinateRemap3D(coors, ((0, 0, 0), (1, 1, 1)))
                print(preprocessing.getEdge3D(coors))
                print(preprocessing.coordinateRemap3D(coors, ((0, 0, 0), (1, 1, 1))))

                with open(r'datasets/pinch0.txt', 'a') as f:
                    f.write(f'{str(coors)}\n')

                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
