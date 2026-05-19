import cv2

def check_camera_index_3():
    print("इंडेक्स ३ वरील कॅमेरा तपासत आहे...")
    
    # थेट इंडेक्स ३ वापरून कॅमेरा सुरू करणे (Iriun सहसा इथेच असतो)
    cap = cv2.VideoCapture(3)
    
    if cap.isOpened():
        print("Index 3 वर कॅमेरा यशस्वीरित्या सापडला आहे!")
        window_name = "Camera Index 3 Preview"
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("फ्रेम वाचता येत नाहीये, कृपया कनेक्शन तपासा.")
                break
            
            # प्रीव्ह्यू विंडोमध्ये व्हिडिओ दाखवणे
            cv2.imshow(window_name, frame)
            
            # 'q' दाबल्यावर विंडो बंद होईल
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Index 3 वर कोणताही कॅमेरा उपलब्ध नाही. इंडेक्स ० किंवा २ तपासून बघा.")

check_camera_index_3()