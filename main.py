import cv2
import numpy as np
import pyautogui
import threading

# Initialize color ranges
npc_lower_color = None
npc_upper_color = None
player_lower_color = None
player_upper_color = None
frame = None
npc_position = None
player_position = None

def pick_color(event, x, y, flags, param):
    global npc_lower_color, npc_upper_color, player_lower_color, player_upper_color
    if event == cv2.EVENT_LBUTTONDOWN:
        color = frame[y, x]
        color_hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]

        if param == "npc":
            npc_lower_color = np.array([color_hsv[0] - 10, 100, 100])
            npc_upper_color = np.array([color_hsv[0] + 10, 255, 255])
            print(f"NPC Color picked: Lower-{npc_lower_color}, Upper-{npc_upper_color}")

        elif param == "player":
            player_lower_color = np.array([color_hsv[0] - 10, 100, 100])
            player_upper_color = np.array([color_hsv[0] + 10, 255, 255])
            print(f"Player Color picked: Lower-{player_lower_color}, Upper-{player_upper_color}")

def detect_object(frame, lower_color, upper_color):
    if lower_color is None or upper_color is None:
        return None

    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the color range
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Get the largest contour (assumed to be the object)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x + w // 2, y + h // 2)  # Return the center of the object
    return None

def move_character():
    global npc_position, player_position
    while True:
        if npc_position and player_position:
            target_x, target_y = npc_position
            player_x, player_y = player_position

            # Calculate the direction to move
            move_x = target_x - player_x
            move_y = target_y - player_y

            # Move the character
            if move_x > 0:
                pyautogui.keyDown('right')
            elif move_x < 0:
                pyautogui.keyDown('left')

            if move_y > 0:
                pyautogui.keyDown('down')
            elif move_y < 0:
                pyautogui.keyDown('up')

            pyautogui.keyUp('right')
            pyautogui.keyUp('left')
            pyautogui.keyUp('down')
            pyautogui.keyUp('up')

def detect_positions():
    global npc_position, player_position, frame
    while True:
        # Capture the screen
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Detect NPC and Player
        npc_position = detect_object(frame, npc_lower_color, npc_upper_color)
        player_position = detect_object(frame, player_lower_color, player_upper_color)

def main():
    global frame

    # Color picking phase
    cap = cv2.VideoCapture(0)
    print("Click on the NPC to set its color.")
    while npc_lower_color is None or npc_upper_color is None:
        ret, frame = cap.read()
        cv2.imshow('Pick NPC Color', frame)
        cv2.setMouseCallback('Pick NPC Color', pick_color, param="npc")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Click on the Player to set its color.")
    while player_lower_color is None or player_upper_color is None:
        ret, frame = cap.read()
        cv2.imshow('Pick Player Color', frame)
        cv2.setMouseCallback('Pick Player Color', pick_color, param="player")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cap.release()

    # Start threads for detection and movement
    detection_thread = threading.Thread(target=detect_positions)
    movement_thread = threading.Thread(target=move_character)

    detection_thread.start()
    movement_thread.start()

    detection_thread.join()
    movement_thread.join()

    while True:
        # Display the frame (optional for debugging)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()