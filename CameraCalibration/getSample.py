import cv2 as cv


cap = cv.VideoCapture(0)

imgNum = 17
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

    cv.imshow('cap', image)  # cv.flip(image, 1)

    k = cv.waitKey(1)

    if k == ord('s'):
        cv.imwrite(f'{imgNum}.jpg', image)
        imgNum += 1
    # if cv.waitKey(5) & 0xFF == 27:
    #     break
cap.release()




