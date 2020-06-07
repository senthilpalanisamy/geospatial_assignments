import math
import numpy as np
import cv2

def LLAtoECEF(phi, lamda, h):
    a = 6378137
    b =  6356752.3142
    f = (a - b) / a
    e = math.sqrt(f * (2-f))
    N_phi = a / math.sqrt(1 - e**2 * (math.sin(math.radians(phi)))**2)
    X = (h + N_phi) * math.cos(math.radians(lamda)) * math.cos(math.radians(phi))
    Y = (h + N_phi) * math.cos(math.radians(phi)) * math.sin(math.radians(lamda))
    Z = (h + (b**2 / a**2) * N_phi) * math.sin(math.radians(phi))
    return X,Y,Z

def ECEFtoENU(X, Y, Z, camera_parameters):
    phi, lamda, h = camera_parameters[:3]
    X0, Y0, Z0 = LLAtoECEF(phi, lamda, h)
    phi, lamda = [math.radians(phi), math.radians(lamda)]
    D_Point = np.array([X - X0, Y - Y0, Z - Z0])
    R = np.array([[-math.sin(lamda), math.cos(lamda), 0],
                  [-math.cos(lamda)* math.sin(phi),-math.sin(phi)*math.sin(lamda), math.cos(phi)],
                  [math.cos(phi)*math.cos(lamda), math.cos(phi)*math.sin(lamda), math.sin(phi)]])
    answer = R.dot(D_Point)
    e,n,u = answer
    return e,n,u

def ENUtoCameraCoordinates(e,n,u, camera_parameters):
    qs, qx, qy, qz = camera_parameters[3:]
    Rq = np.array([[1-2*(qy**2+qz**2), 2*qx*qy-2*qs*qz, 2*qx*qz+2*qs*qy],
                   [2*qx*qy+2*qs*qz, 1-2*(qx**2+qz**2), 2*qy*qz-2*qs*qx],
                   [2*qx*qz-2*qs*qy, 2*qy*qz+2*qs*qx, 1-2*(qx**2+qy**2)]])
    answer = Rq.dot(np.array([e,n,-u]))
    x,y,z = answer
    return x,y,z

def CameraCoordinatestoImageCoorinatesFront(x, y, z, Rs=2048):
    xi = y / z * (Rs - 1)/ 2.0 + (Rs + 1) /2
    yi = x / z  * (Rs - 1)/ 2.0 + (Rs + 1) / 2
    return xi, yi

def CameraCoordinatestoImageCoorinatesBack(x, y, z, Rs=2048):
    xi = - y / z * (Rs - 1)/ 2.0 + (Rs + 1) /2
    yi = - x / z  * (Rs - 1)/ 2.0 + (Rs + 1) / 2


    return xi, yi

def CameraCoordinatestoImageCoorinatesLeft(x, y, z, Rs=2048):
    xi = - y / x * (Rs - 1)/ 2.0 + (Rs + 1) /2
    yi =  - z / x  * (Rs - 1)/ 2.0 + (Rs + 1) / 2
    return xi, yi

def CameraCoordinatestoImageCoorinatesRight(x, y, z, Rs=2048):
    xi = y / x * (Rs - 1)/ 2.0 + (Rs + 1) /2
    yi =   -z / x  * (Rs - 1)/ 2.0 + (Rs + 1) / 2
    return xi, yi

def unit_test():
    lat =  45.9038834
    lon = 11.02841352
    height =  232.4648
    X, Y, Z = LLAtoECEF(lat, lon, height)
    answer = [4364.051, 850.532, 4557.987]
    assert abs(X/1000.0 - answer[0]) < 1e-1
    assert abs(Y/1000.0 - answer[1]) < 1e-1
    assert abs(Z/1000.0 - answer[2]) < 1e-1

    camera_parameters = [45.9132, 36.7484, 1877753.2]
    X, Y, Z = [5507528.9, 4556224.1,6012820.8]
    e,n,u = ECEFtoENU(X, Y, Z, camera_parameters)
    answer = [355.6013, -923.0832, 1.0410e+03]
    assert abs(answer[0] - e/1000.0) < 1e-1
    assert abs(answer[1] - n/1000.0) < 1e-1
    assert abs(answer[2] - u/1000.0) < 1
    #print('here')


if __name__=='__main__':
    unit_test()
    Rs = 4000
    front_image = np.zeros((Rs, Rs), dtype = np.uint8)
    left_image = np.zeros((Rs, Rs), dtype = np.uint8)
    right_image = np.zeros((Rs, Rs), dtype = np.uint8)
    back_image = np.zeros((Rs, Rs), dtype = np.uint8)
    camera_params_file_path = '/home/senthilpalanisamy/Downloads/final_project_data (2)/image/camera.config'
    with open(camera_params_file_path, 'r') as camera_params_file:
        _ = camera_params_file.readline()
        camera_params = camera_params_file.readline()
        camera_params = camera_params.split(',')
        camera_params = [float(x) for x in camera_params]

    point_cloud_file_path = '/home/senthilpalanisamy/Downloads/final_project_data (2)/final_project_point_cloud.fuse'
    count = 0
    with open(point_cloud_file_path, 'r') as point_file:
        #point = point_file.readline()
        for point in point_file:
          point = point.split(' ')
          point = [float(x) for x in point]
          intensity = point[3]
          X, Y, Z = LLAtoECEF(*point[:3])
          e, n, u = ECEFtoENU(X, Y, Z, camera_params)
          x, y, z =ENUtoCameraCoordinates(e, n, u, camera_params)




          #if(z > abs(y)):
          if(z > 0 and z > abs(x) and z > abs(y)):
          #if(z > -x and z > x):
              xi, yi = CameraCoordinatestoImageCoorinatesFront(x, y, z, Rs)
              xi, yi = int(xi), int(yi)

              front_image[yi, xi] = intensity

          if(x < 0 and x < -abs(z) and x < -abs(y)):
          #elif(z < -x and z > x):
              xi, yi = CameraCoordinatestoImageCoorinatesLeft(x, y, z, Rs)
              xi, yi = int(xi), int(yi)

              left_image[yi, xi] = intensity

          if(z < 0 and z < -abs(x) and z < -abs(y)):
          #elif(z<x and z < -x):
              xi, yi = CameraCoordinatestoImageCoorinatesBack(x, y, z, Rs)
              xi, yi = int(xi), int(yi)

              back_image[yi, xi] = intensity

          if(x > 0 and x > abs(y) and x > abs(z)):
          #elif(z > -x and z < x):
              xi, yi = CameraCoordinatestoImageCoorinatesRight(x, y, z, Rs)
              xi, yi = int(xi), int(yi)

              right_image[yi, xi] = intensity

    front_image = cv2.equalizeHist(front_image) 
    back_image = cv2.equalizeHist(back_image) 
    left_image = cv2.equalizeHist(left_image) 
    right_image = cv2.equalizeHist(right_image) 
 
 
    cv2.imshow('front', front_image)
    cv2.imshow('back', back_image)
    cv2.imshow('left', left_image)
    cv2.imshow('right', right_image)
    cv2.waitKey(0)


    cv2.imwrite('front_image.jpg', front_image)
    cv2.imwrite('back_image.jpg', back_image)
    cv2.imwrite('left_image.jpg', left_image)
    cv2.imwrite('right_image.jpg', right_image)





