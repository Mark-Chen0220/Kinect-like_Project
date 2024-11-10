import cv2
import mediapipe as mp
import pydirectinput
import time

# Initialize MediaPipe Pose, keyboard and mouse controllers, and webcam
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

def detect_gesture(landmarks):
    forward_threshold = 0.05
    left_threshold = 0.2
    right_threshold = 0.2

#Origin Point is top-right corner
#For Z coords, the closer it is, the smaller the value
    # Define movement based on body landmarks
    if ((landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y - landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y) > forward_threshold
            or (landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y - landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y) > forward_threshold):
        return "move_forward"
    if (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z - landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z) > left_threshold:
        return "move_left"
    if (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z - landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z) > right_threshold:
        return "move_right"
    if landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y < landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y:
        return "left_click"  # Attack if right hand is raised above the shoulder
    if (landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].z - landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z) > -0.4:
        return "hold_right"   # Bow pose
    if (landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z - landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].z) > -0.5:
        return "hold_left"   # Punch tree
    if landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y < landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y:
        return "right_click"  # Open chest if left hand is raised above the elbow
    return "idle"


#tap left click
#tap right click
#hold right click
#
def movement_action(action):
    if action == "move_forward":
        pydirectinput.keyDown('w')
    elif action == "move_left":
        pydirectinput.keyDown('a')
    elif action == "move_right":
        pydirectinput.keyDown('d')
    else:
        pydirectinput.keyUp('a')
        pydirectinput.keyUp('d')
        pydirectinput.keyUp('w')

def hold_left(action):
    if action == "hold_left":
        pydirectinput.mouseDown(button="left")
    else:
        pydirectinput.mouseUp(button="left")
def hold_right(action):
    if action == "hold_right":
        pydirectinput.mouseDown(button="right")
    else:
        pydirectinput.mouseUp(button="right")

def click(action):
    if action == "left_click":
        pydirectinput.leftClick()
    elif action == "right_click":
        pydirectinput.rightClick()  

def print_action(action):
    if action == "left_click":
        print("Attack")
    elif action == "right_click":
        print("Right Click")
    elif action == "hold_right":
        print("Charge_Bow")
    elif action == "hold_left":
        print("Destroying Block")
    elif action == "move_left":
        print("Left")
    elif action == "move_right":
        print("Right")
    elif action == "move_forward":
        print("Forward")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        action = detect_gesture(landmarks)
        movement_action(action)  # Perform action based on detected gesture
        hold_left(action)
        hold_right(action)
        click(action)
        print_action(action)    # Print the action for visualization
        #print("Right-Left: ")
        #print(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].z - landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].z)

        # Draw landmarks on the frame
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("Minecraft Motion Control", frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()