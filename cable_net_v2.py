#!/usr/bin/env python
# -*- coding: UTF-8 -*-


'''
Name： NetPanelAnalysis
Function: 计算柔性防护系统中任意四边形钢丝绳网片顶破力、顶破位移、耗能能力
Note: 国际单位制
Version: 1.2.1
Author: Liping GUO
Date: from 2021/8/31 to 
命名方式：以平行于x方向及y方向分别作为后缀
Remark: 尚未解决的问题：
	(1)考虑矩形之外的网孔形状
	(2)考虑柔性边界刚度
'''

import numpy as np
from userfunc_NPA import *


######################################################################################################################################################
# 本部分代码用于校准另一种方法
def func_cablenet_xyz(theta, H, w, Rp, Rs, a, m):
	i_arr = np.arange(1,m+0.1,step=1)

	xP_arr = a/2*(2*i_arr - m - 1)
	yP_arr = np.sqrt(Rp**2 - xP_arr**2)
	zP_arr = H*np.ones_like(xP_arr)

	theta_1 = np.arcsin(xP_arr[-1]/(w/np.sqrt(2)))
	theta_2 = np.arccos(xP_arr[-1]/(w/np.sqrt(2)))
	if theta>=0 and theta<theta_1:
		m1 = int(m/2 - 1/2*func_round(np.sqrt(2)*w*np.sin(theta)/a))

		i1_arr = np.arange(1,m1+0.1,step=1)
		i2_arr = np.arange(m1+1,m+0.1,step=1)
		yQ1_arr = w/np.sqrt(2)*np.cos(theta) - abs(xP_arr[0] +w/np.sqrt(2)*np.sin(theta))*np.tan(np.pi/4+theta) + a*(i1_arr-1)*np.tan(np.pi/4+theta)
		yQ2_arr = w/np.sqrt(2)*np.cos(theta) - abs(xP_arr[m1]+w/np.sqrt(2)*np.sin(theta))*np.tan(np.pi/4-theta) - a*(i2_arr-m1-1)*np.tan(np.pi/4-theta)
	
		xQ_arr = xP_arr
		yQ_arr = np.concatenate((yQ1_arr,yQ2_arr))
		zQ_arr = np.zeros_like(xP_arr)

	elif theta>=theta_1 and theta<=theta_2:
		xQ_arr = xP_arr
		yQ_arr = w/np.sqrt(2)*np.cos(theta) - abs(xP_arr[0] +w/np.sqrt(2)*np.sin(theta))*np.tan(np.pi/4-theta) - a*(i_arr-1)*np.tan(np.pi/4-theta)
		zQ_arr = np.zeros_like(xP_arr)

	elif theta>theta_2 and theta<np.pi/2:
		m1 = m/2 - 1/2*func_round(np.sqrt(2)*w*np.cos(theta)/a)

		i1_arr = np.arange(1,m1+0.1,step=1)
		i2_arr = np.arange(m1+1,m+0.1,step=1)
		yQ1_arr = w/np.sqrt(2)*np.sin(theta) - abs(xP_arr[0] -w/np.sqrt(2)*np.cos(theta))*np.tan(theta-np.pi/4) + a*(i1_arr-1)*np.tan(theta-np.pi/4)
		yQ2_arr = w/np.sqrt(2)*np.sin(theta) - abs(xP_arr[m1]-w/np.sqrt(2)*np.cos(theta))*np.tan(3*np.pi/4-theta) - a*(i2_arr-m1-1)*np.tan(3*np.pi/4-theta)
			
		xQ_arr = xP_arr
		yQ_arr1 = np.concatenate((yQ1_arr,yQ2_arr))
		zQ_arr = np.zeros_like(xP_arr)
	else:
		raise ValueError

	Lu_PQ = np.sqrt((xQ_arr-xP_arr)**2 + (yQ_arr-yP_arr)**2 + (zQ_arr-zP_arr)**2)
	Ld_PQ = Lu_PQ[::-1]

	if H == 0:
		Lc_PQ = 2*yP_arr
	else:
		Lc_PQ = 2*np.sqrt(Rs**2-xP_arr**2) * np.arctan(np.sqrt(Rp**2-xP_arr**2)/np.sqrt(Rs**2-Rp**2))		

	return Lu_PQ, Lc_PQ, Ld_PQ
######################################################################################################################################################


def func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_PlusX,m_PlusX,a_PlusY,m_PlusY,Rs,Rp,H):
	h = Rs-np.sqrt(Rs**2-Rp**2)  # 加载顶头自身高度
	if H>=0.0 and H < h:
		Rp_H = np.sqrt(Rs**2-(Rs-H)**2)
	elif H>=h:
		Rp_H = Rp
	else:
		raise ValueError

	i_PlusY = np.arange(1,m_PlusY1,step=1)
	
	xP_PlusY = a_PlusY/2*(2*i_PlusY - m_PlusY - 1)
	yP_PlusY = np.sqrt(Rp**2 - xP_PlusY**2)
	zP_PlusY = H*np.ones_like(xP_PlusY)

	xP_MinusY = xP_PlusY
	yP_MinusY = -yP_PlusY
	zP_MinusY = zP_PlusY

	xQ_PlusY,xQ_MinusY = xP_PlusY,xP_PlusY
	yQ_PlusY,yQ_MinusY = np.zeros_like(xP_PlusY),np.zeros_like(xP_PlusY)
	zQ_PlusY,zQ_MinusY = np.zeros_like(xP_PlusY),np.zeros_like(xP_PlusY)

	for i in range(len(xP_PlusY)):
		if abs(xP_PlusY[i])<Rp_H:
			yP_PlusY[i] = np.sqrt(Rp_H**2 - xP_PlusY[i]**2)
			yP_MinusY[i] = -yP_PlusY[i]
		else:
			pass

		if (xP_PlusY[i]>x1 and xP_PlusY[i]<x2) or (xP_PlusY[i]<x1 and xP_PlusY[i]>x2):
			yQ_Y = y1 + (xP_PlusY[i]-x1)*(y2-y1)/(x2-x1)
			if yQ_Y>yP_PlusY[i]:
				yQ_PlusY[i] = yQ_Y
			elif yQ_Y<yP_MinusY[i]:
				yQ_MinusY[i] = yQ_Y
			else:
				raise ValueError
		else:
			pass

		if (xP_PlusY[i]>x2 and xP_PlusY[i]<x3) or (xP_PlusY[i]<x2 and xP_PlusY[i]>x3):
			yQ_Y =  y2 + (xP_PlusY[i]-x2)*(y3-y2)/(x3-x2)
			if yQ_Y>yP_PlusY[i]:
				yQ_PlusY[i] = yQ_Y
			elif yQ_Y<yP_MinusY[i]:
				yQ_MinusY[i] = yQ_Y
			else:
				raise ValueError
		else:
			pass

		if (xP_PlusY[i]>x3 and xP_PlusY[i]<x4) or (xP_PlusY[i]<x3 and xP_PlusY[i]>x4):
			yQ_Y =  y3 + (xP_PlusY[i]-x3)*(y4-y3)/(x4-x3)
			if yQ_Y>yP_PlusY[i]:
				yQ_PlusY[i] = yQ_Y
			elif yQ_Y<yP_MinusY[i]:
				yQ_MinusY[i] = yQ_Y
			else:
				raise ValueError
		else:
			pass

		if (xP_PlusY[i]>x4 and xP_PlusY[i]<x1) or (xP_PlusY[i]<x4 and xP_PlusY[i]>x1):
			yQ_Y =  y4 + (xP_PlusY[i]-x4)*(y1-y4)/(x1-x4)
			if yQ_Y>yP_PlusY[i]:
				yQ_PlusY[i] = yQ_Y
			elif yQ_Y<yP_MinusY[i]:
				yQ_MinusY[i] = yQ_Y
			else:
				raise ValueError
		else:
			pass

	j_PlusX = np.arange(1,m_PlusX+0.1,step=1)
	yP_PlusX = a_PlusX/2*(2*j_PlusX - m_PlusX - 1)
	xP_PlusX = np.sqrt(Rp**2 - yP_PlusX**2)
	zP_PlusX = H*np.ones_like(yP_PlusX)

	yP_MinusX = yP_PlusX
	xP_MinusX = -xP_PlusX
	zP_MinusX = zP_PlusX

	yQ_PlusX,yQ_MinusX = yP_PlusX,yP_PlusX
	xQ_PlusX,xQ_MinusX = np.zeros_like(yP_PlusX),np.zeros_like(yP_PlusX)
	zQ_PlusX,zQ_MinusX = np.zeros_like(yP_PlusX),np.zeros_like(yP_PlusX)

	for j in range(len(yP_PlusX)):

		if abs(yP_PlusX[j])<Rp_H:
			xP_PlusX[j] = np.sqrt(Rp_H**2 - yP_PlusX[j]**2)
			xP_MinusX[j] = -xP_PlusX[j]
		else:
			pass

		if (yP_PlusX[j]>y1 and yP_PlusX[j]<y2) or (yP_PlusX[j]<y1 and yP_PlusX[j]>y2):
			xQ_X = x1 + (yP_PlusX[j] - y1)*(x2-x1)/(y2-y1)
			if xQ_X > xP_PlusX[j]:
				xQ_PlusX[j] = xQ_X
			elif xQ_X < xP_MinusX[j]:
				xQ_MinusX[j] = xQ_X
			else:
				raise ValueError
		else:
			pass

		if (yP_PlusX[j]>y2 and yP_PlusX[j]<y3) or (yP_PlusX[j]<y2 and yP_PlusX[j]>y3):
			xQ_X = x2 + (yP_PlusX[j] - y2)*(x3-x2)/(y3-y2)
			if xQ_X > xP_PlusX[j]:
				xQ_PlusX[j] = xQ_X
			elif xQ_X < xP_MinusX[j]:
				xQ_MinusX[j] = xQ_X
			else:
				raise ValueError
		else:
			pass

		if (yP_PlusX[j]>y3 and yP_PlusX[j]<y4) or (yP_PlusX[j]<y3 and yP_PlusX[j]>y4):
			xQ_X = x3 + (yP_PlusX[j] - y3)*(x4-x3)/(y4-y3)
			if xQ_X > xP_PlusX[j]:
				xQ_PlusX[j] = xQ_X
			elif xQ_X < xP_MinusX[j]:
				xQ_MinusX[j] = xQ_X
			else:
				raise ValueError
		else:
			pass

		if (yP_PlusX[j]>y4 and yP_PlusX[j]<y1) or (yP_PlusX[j]<y4 and yP_PlusX[j]>y1):
			xQ_X =  x4 + (yP_PlusX[j] - y4)*(x1-x4)/(y1-y4)
			if xQ_X > xP_PlusX[j]:
				xQ_PlusX[j] = xQ_X
			elif xQ_X < xP_MinusX[j]:
				xQ_MinusX[j] = xQ_X
			else:
				raise ValueError
		else:
			pass

	length_PQ_PlusX = np.sqrt((xP_PlusX-xQ_PlusX)**2+(yP_PlusX-yQ_PlusX)**2+(zP_PlusX-zQ_PlusX)**2)
	length_PQ_PlusY = np.sqrt((xP_PlusY-xQ_PlusY)**2+(yP_PlusY-yQ_PlusY)**2+(zP_PlusY-zQ_PlusY)**2)
	length_PQ_MinusX = np.sqrt((xP_MinusX-xQ_MinusX)**2+(yP_MinusX-yQ_MinusX)**2+(zP_MinusX-zQ_MinusX)**2)
	length_PQ_MinusY = np.sqrt((xP_MinusY-xQ_MinusY)**2+(yP_MinusY-yQ_MinusY)**2+(zP_MinusY-zQ_MinusY)**2)

	return length_PQ_PlusX, length_PQ_MinusX, length_PQ_PlusY, length_PQ_MinusY

def func_Pxyz(x1,y1,x2,y2,x3,y3,x4,y4,a_PlusX,m_PlusX,a_PlusY,m_PlusY,Rs,Rp,H):
	h = Rs-np.sqrt(Rs**2-Rp**2)  # 加载顶头自身高度
	if H>=0.0 and H < h:
		Rp_H = np.sqrt(Rs**2-(Rs-H)**2)
	elif H>=h:
		Rp_H = Rp
	else:
		raise ValueError

	i_Plus1 = np.arange(1,m_Plus1+0.1,step=1)

	yP_Plus1 = a_Plus1/2*(2*i_Plus1 - m_Plus1 - 1)
	xP_Plus1 = np.sqrt(Rp**2 - yP_Plus1**2)
	zP_Plus1 = H*np.ones_like(yP_Plus1)

	yP_Minu1 = yP_Plus1
	xP_Minu1 = -xP_Plus1
	zP_Minu1 = zP_Plus1

	xP_Plus1_rotate = xP_Plus1*np.cos(alpha1) - yP_Plus1*np.sin(alpha1)
	yP_Plus1_rotate = xP_Plus1*np.sin(alpha1) + yP_Plus1*np.cos(alpha1)
	zP_Plus1_rotate = zP_Plus1

	xP_Minu1_rotate = xP_Minu1*np.cos(alpha1) - yP_Minu1*np.sin(alpha1)
	yP_Minu1_rotate = xP_Minu1*np.sin(alpha1) + yP_Minu1*np.cos(alpha1)
	zP_Minu1_rotate = zP_Minu1

	return xP_Plus1_rotate, yP_Plus1_rotate, zP_Plus1_rotate, xP_Minu1_rotate, yP_Minu1_rotate, zP_Minu1_rotate


def func_cross_line_point(A1, B1, C1, A2, B2, C2):
	x_cross = (B1*C2-B2*C1)/(A1*B2-A2*B1)
	y_cross = (A2*C1-A1*C2)/(A1*B2-A2*B1)
	return x_cross, y_cross

def func_Qxyz(xP_Plus, yP_Plus, zP_Plus, xP_Minu, yP_Minu, zP_Minu):
	# 以下A B C均为只想方程Ax+By+C = 0的系数
	A1_arr = (yP_Plus-yP_Minu)/(xP_Plus-xP_Minu)
	B1_arr = -1+np.zeros_like(A1_arr)
	C1_arr = yP_Minu-(yP_Plus-yP_Minu)/(xP_Plus-xP_Minu)*xP_Minu

	A2_line12 = (y2-y1)/(x2-x1)
	B2_line12 = -1+np.zeros_like(A2_line12)
	C2_line12 = y1-(y2-y1)/(x2-x1)*x1
	xQ_line12 = (B1_arr*C2_line12-B2_line12*C1_arr)/(A1_arr*B2_line12-A2_line12*B1_arr)
	yQ_line12 = (A2_line12*C1_arr-A1_arr*C2_line12)/(A1_arr*B2_line12-A2_line12*B1_arr)

	A2_line23 = (y3-y2)/(x3-x2)
	B2_line23 = -1+np.zeros_like(A2_line23)
	C2_line23 = y2-(y3-y2)/(x3-x2)*x2
	xQ_line23 = (B1_arr*C2_line23-B2_line23*C1_arr)/(A1_arr*B2_line23-A2_line23*B1_arr)
	yQ_line23 = (A2_line23*C1_arr-A1_arr*C2_line23)/(A1_arr*B2_line23-A2_line23*B1_arr)

	A2_line34 = (y4-y3)/(x4-x3)
	B2_line34 = -1+np.zeros_like(A2_line34)
	C2_line34 = y3-(y4-y3)/(x4-x3)*x3
	xQ_line34 = (B1_arr*C2_line34-B2_line34*C1_arr)/(A1_arr*B2_line34-A2_line34*B1_arr)
	yQ_line34 = (A2_line34*C1_arr-A1_arr*C2_line34)/(A1_arr*B2_line34-A2_line34*B1_arr)

	A2_line41 = (y4-y1)/(x4-x1)
	B2_line41 = -1+np.zeros_like(A2_line41)
	C2_line41 = y1-(y4-y1)/(x4-x1)*x1
	xQ_line41 = (B1_arr*C2_line41-B2_line41*C1_arr)/(A1_arr*B2_line41-A2_line41*B1_arr)
	yQ_line41 = (A2_line41*C1_arr-A1_arr*C2_line41)/(A1_arr*B2_line41-A2_line41*B1_arr)

	for i1 in range(m1):
		for i12 in range(xQ_line12):
			if xQ_line12[i12]<x1 and xQ_line12[i12]<x2:
				pass
			elif  xQ_line12[i12]>x1 and xQ_line12[i12]>x2:
				pass
			else:
				xQ1[i1] = xQ_line12[i12]
		for i23 in range(xQ_line23):
			if xQ_line23[i23]<x2 and xQ_line23[i23]<x3:
				pass
			elif  xQ_line23[i23]>x2 and xQ_line23[i23]>x3:
				pass
			else:
				xQ1[i1] = xQ_line23[i23]
		for i34 in range(xQ_line34):
			if xQ_line34[i34]<x3 and xQ_line34[i34]<x4:
				pass
			elif  xQ_line34[i34]>x3 and xQ_line34[i34]>x4:
				pass
			else:
				xQ1[i1] = xQ_line34[i34]				
		for i41 in range(xQ_line41):
			if xQ_line41[i41]<x1 and xQ_line41[i41]<x4:
				pass
			elif  xQ_line41[i41]>x1 and xQ_line41[i41]>x4:
				pass
			else:
				xQ1[i1] = xQ_line41[i41]


def func_lengthArc(H,Rs,Rp,a_DireX,m_DireX,a_DireY,m_DireY):
	i_DireX = np.arange(1,m_DireX+0.1,step=1)
	i_DireY = np.arange(1,m_DireY+0.1,step=1)

	d_DireX = abs(a_DireX/2*(2*i_DireX - m_DireX - 1))
	d_DireY = abs(a_DireY/2*(2*i_DireY - m_DireY - 1))

	minH = Rs-np.sqrt(Rs**2-Rp**2)
	if H>0.0 and H < minH:
		Rp_H = np.sqrt(Rs**2-(Rs-H)**2)
		beta_DireX = np.zeros_like(d_DireX)
		beta_DireY = np.zeros_like(d_DireY)
		arc_length_DireX = np.zeros_like(d_DireX)
		arc_length_DireY = np.zeros_like(d_DireY)

		for iDX in range(len(d_DireX)):
			if abs(d_DireX[iDX])<Rp_H:
				beta_DireX[iDX] = 2*np.arccos((Rs-H)/np.sqrt(Rs**2-d_DireX[iDX]**2))
				arc_length_DireX[iDX] = beta_DireX[iDX]*np.sqrt(Rs**2-d_DireX[iDX]**2)
			else:
				arc_length_DireX[iDX] = 2*np.sqrt(Rp**2 - d_DireX[iDX]**2)
		
		for iDY in range(len(d_DireY)):
			if abs(d_DireY[iDY])<Rp_H:
				beta_DireY[iDY] = 2*np.arccos((Rs-H)/np.sqrt(Rs**2-d_DireY[iDY]**2))
				arc_length_DireY[iDY] = beta_DireY[iDY]*np.sqrt(Rs**2-d_DireY[iDY]**2)
			else:
				arc_length_DireY[iDY] = 2*np.sqrt(Rp**2 - d_DireY[iDY]**2)

	elif H >= minH:
		alpha_DireX = 2*np.arctan(np.sqrt((Rp**2-d_DireX**2)/(Rs**2-Rp**2)))
		alpha_DireY = 2*np.arctan(np.sqrt((Rp**2-d_DireY**2)/(Rs**2-Rp**2)))
		arc_length_DireX = alpha_DireX*np.sqrt(Rs**2-d_DireX**2)
		arc_length_DireY = alpha_DireY*np.sqrt(Rs**2-d_DireY**2)
	elif H == 0.0:
		arc_length_DireX = 2*np.sqrt(Rp**2 - d_DireX**2)
		arc_length_DireY = 2*np.sqrt(Rp**2 - d_DireY**2)
	else:
		raise ValueError
	return arc_length_DireX,arc_length_DireY

def func_sigma(epsilon, sigma_y, E1, E2):
	epsilon1 = sigma_y/E1
	sigma_XY = np.zeros_like(epsilon)
	for i in range (int(len(epsilon))):
		if epsilon[i]>=0 and epsilon[i]<=epsilon1:
			sigma_XY[i] = E1*epsilon[i]
		elif epsilon[i]>epsilon1:
			sigma_XY[i] = sigma_y+E2*(epsilon[i]-epsilon1)
		elif epsilon[i]<0:
			pass
		else:
			raise ValueError
	return sigma_XY


# 参数输入----------------------------------------------------------------------------------- #
if __name__ == '__main__':

	d1, d2 = 0.3, 0.3  # 本程序可以用于计算两侧不同的a值（网孔间距）
	alpha1, alpha2 = 0, np.pi/2

	ex, ey = 0, 0
	Rs = 1.2  # 球罐形加载顶头半径
	Rp = 0.5  # 加载顶头水平投影半径，若加载形状为多边形时考虑为半径为Rp圆内切

	n_loop = 0 # 初始增量步数
	epsilon_max = 0.0  # 钢丝绳初始应变
	epsilon_f = 0.0235  # 钢丝绳失效应变
	init_H = 0.55  # 钢丝绳网初始挠度（初始高度)
	step_H = 1e-3  # 网片位移加载增量步长，单位：m
	Height = 0.0  # 网片加载位移

	m1 = 2*func_round(Rp/d1)  # 第1方向上与加载区域相交的钢丝绳数量（偶数）
	m2 = 2*func_round(Rp/d2)  # 第2方向上与加载区域相交的钢丝绳数量（偶数）

	#x1, y1 = 1.5*np.sqrt(2), 0
	#x2, y2 = 0, 1.5*np.sqrt(2)
	#x3, y3 = -1.5*np.sqrt(2), 0
	#x4, y4 = 0, -1.5*np.sqrt(2)

	x1, y1 = 1.5, 0
	x2, y2 = 0, 1.5
	x3, y3 = -1.5, 0
	x4, y4 = 0, -1.5

	E1, E2 = 91.304e9, 25.0e9
	sigma_y = 1050e6
	sigma_f = 1350e6
	fail_force = 40700
	A_rope = fail_force/sigma_f



	m_Plus1 = m1
	a_Plus1 = d1
	H = 0
	i_Plus1 = np.arange(1,m_Plus1+0.1,step=1)  # 第一方向上与加载区域相交的钢丝绳序列（从1开始）
	dist1_arr = d1/2*(2*i_Plus1 - m_Plus1 - 1)

	yP_Plus1 = a_Plus1/2*(2*i_Plus1 - m_Plus1 - 1)
	xP_Plus1 = np.sqrt(Rp**2 - yP_Plus1**2)
	zP_Plus1 = H*np.ones_like(yP_Plus1)

	yP_Minu1 = yP_Plus1
	xP_Minu1 = -xP_Plus1
	zP_Minu1 = zP_Plus1

	xP_Plus = ex + xP_Plus1*np.cos(alpha1) - yP_Plus1*np.sin(alpha1)
	yP_Plus = ey + xP_Plus1*np.sin(alpha1) + yP_Plus1*np.cos(alpha1)
	zP_Plus = zP_Plus1

	xP_Minu = ex + xP_Minu1*np.cos(alpha1) - yP_Minu1*np.sin(alpha1)
	yP_Minu = ey + xP_Minu1*np.sin(alpha1) + yP_Minu1*np.cos(alpha1)
	zP_Minu = zP_Minu1

	print('xP_Minu=',xP_Minu)







	A1_arr = (yP_Plus-yP_Minu)/(xP_Plus-xP_Minu)
	B1_arr = -1+np.zeros_like(A1_arr)
	C1_arr = yP_Minu-(yP_Plus-yP_Minu)/(xP_Plus-xP_Minu)*xP_Minu

	A2_line12 = (y2-y1)/(x2-x1)
	B2_line12 = -1+np.zeros_like(A2_line12)
	C2_line12 = y1-(y2-y1)/(x2-x1)*x1
	xQ_line12 = (B1_arr*C2_line12-B2_line12*C1_arr)/(A1_arr*B2_line12-A2_line12*B1_arr)
	yQ_line12 = (A2_line12*C1_arr-A1_arr*C2_line12)/(A1_arr*B2_line12-A2_line12*B1_arr)

	A2_line23 = (y3-y2)/(x3-x2)
	B2_line23 = -1+np.zeros_like(A2_line23)
	C2_line23 = y2-(y3-y2)/(x3-x2)*x2
	xQ_line23 = (B1_arr*C2_line23-B2_line23*C1_arr)/(A1_arr*B2_line23-A2_line23*B1_arr)
	yQ_line23 = (A2_line23*C1_arr-A1_arr*C2_line23)/(A1_arr*B2_line23-A2_line23*B1_arr)

	A2_line34 = (y4-y3)/(x4-x3)
	B2_line34 = -1+np.zeros_like(A2_line34)
	C2_line34 = y3-(y4-y3)/(x4-x3)*x3
	xQ_line34 = (B1_arr*C2_line34-B2_line34*C1_arr)/(A1_arr*B2_line34-A2_line34*B1_arr)
	yQ_line34 = (A2_line34*C1_arr-A1_arr*C2_line34)/(A1_arr*B2_line34-A2_line34*B1_arr)

	A2_line41 = (y4-y1)/(x4-x1)
	B2_line41 = -1+np.zeros_like(A2_line41)
	C2_line41 = y1-(y4-y1)/(x4-x1)*x1
	xQ_line41 = (B1_arr*C2_line41-B2_line41*C1_arr)/(A1_arr*B2_line41-A2_line41*B1_arr)
	yQ_line41 = (A2_line41*C1_arr-A1_arr*C2_line41)/(A1_arr*B2_line41-A2_line41*B1_arr)

	xQ1 = np.zeros(2*m1)
	yQ1 = np.zeros(2*m1)
	i1 = 0
	for i12 in range(len(xQ_line12)):
		if xQ_line12[i12]<x1 and xQ_line12[i12]<x2:
			pass
		elif  xQ_line12[i12]>x1 and xQ_line12[i12]>x2:
			pass
		else:
			xQ1[i1] = xQ_line12[i12]
			yQ1[i1] = y1 + (y2-y1)/(x2-x1)*(xQ_line12[i12]-x1)
			i1 = i1 + 1
	for i23 in range(len(xQ_line23)):
		if xQ_line23[i23]<x2 and xQ_line23[i23]<x3:
			pass
		elif  xQ_line23[i23]>x2 and xQ_line23[i23]>x3:
			pass
		else:
			xQ1[i1] = xQ_line23[i23]
			yQ1[i1] = y2 + (y3-y2)/(x3-x2)*(xQ_line23[i23]-x2)
			i1 = i1 + 1
	for i34 in range(len(xQ_line34)):
		if xQ_line34[i34]<x3 and xQ_line34[i34]<x4:
			pass
		elif  xQ_line34[i34]>x3 and xQ_line34[i34]>x4:
			pass
		else:
			xQ1[i1] = xQ_line34[i34]				
			yQ1[i1] = y3 + (y4-y3)/(x4-x3)*(xQ_line34[i34]-x3)
			i1 = i1 + 1
	for i41 in range(len(xQ_line41)):
		if xQ_line41[i41]<x1 and xQ_line41[i41]<x4:
			pass
		elif  xQ_line41[i41]>x1 and xQ_line41[i41]>x4:
			pass
		else:
			xQ1[i1] = xQ_line41[i41]
			yQ1[i1] = y1 + (y4-y1)/(x4-x1)*(xQ_line41[i41]-x1)
			i1 = i1 + 1

	print('xQ1=',xQ1)
	print('yQ1=',yQ1)

	print('xP_Plus1=',xP_Plus1)
	print('yP_Plus1=',yP_Plus1)

	i_plus = 0
	i_minu = 0
	xQ1_Plus = np.zeros(2*m1)
	xQ1_Minu = np.zeros(2*m1)
	yQ1_Plus = np.zeros(2*m1)
	yQ1_Minu = np.zeros(2*m1)
	for i in range(len(xP_Plus1)):
		for j in range(len(xQ1)):
			k_search = (yQ1[j] - yP_Plus1[i])/(xQ1[j] - xP_Plus1[i])
			k_target = (yP_Plus1[i] - yP_Minu1[i])/(xP_Plus1[i] - xP_Minu1[i])
			if abs(k_search-k_target) < 1e-8:
				xQ1_Plus[i+i_plus] = xQ1[j]
				yQ1_Plus[i+i_plus] = yQ1[j]
				print('xQ1_Plus=',xQ1_Plus)
				print('yQ1_Plus=',yQ1_Plus)
				i_plus = i_plus + 1
			else:
				pass
	'''					
	for i in range(len(xP_Plus1)):
		for j in range(len(xQ1)):
			k_search = (yQ1[j] - yP_Plus1[i])/(xQ1[j] - xP_Plus1[i])
			k_target = (yP_Plus1[i] - yP_Minu1[i])/(xP_Plus1[i] - xP_Minu1[i])
			if abs(k_search-k_target) < 1e-8:
				if yQ1[j] >= yP_Plus1[i]:
					xQ1_Plus[i+i_plus] = xQ1[j]
					yQ1_Plus[i+i_plus] = yQ1[j]
					print('xQ1_Plus=',xQ1_Plus)
					print('yQ1_Plus=',yQ1_Plus)
					i_plus = i_plus + 1
				elif yQ1[j] < yP_Plus1[i]:
					xQ1_Minu[i+i_minu] = xQ1[j]
					yQ1_Minu[i+i_minu] = yQ1[j]
					print('xQ1_Minu=',xQ1_Minu)
					print('yQ1_Minu=',yQ1_Minu)
					i_minu = i_minu + 1		
				else:
					raise ValueError			
			else:
				pass
	'''






	xP_dire1_plus = ex + Rp*np.cos(alpha1-np.arcsin(dist1_arr/Rp**2))
	yP_dire1_plus = ey + Rp*np.sin(alpha1-np.arcsin(dist1_arr/Rp**2))

	xP_dire1_minu = ex - Rp*np.cos(alpha1-np.arcsin(dist1_arr/Rp**2))
	yP_dire1_minu = ey - Rp*np.sin(alpha1-np.arcsin(dist1_arr/Rp**2))

	length_PQ_PlusX0  = func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_DireX,m_DireX,a_DireY,m_DireY,Rs,Rp,init_H)[0]
	length_PQ_MinusX0 = func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_DireX,m_DireX,a_DireY,m_DireY,Rs,Rp,init_H)[1]
	length_PQ_PlusY0  = func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_DireX,m_DireX,a_DireY,m_DireY,Rs,Rp,init_H)[2]
	length_PQ_MinusY0 = func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_DireX,m_DireX,a_DireY,m_DireY,Rs,Rp,init_H)[3]

	length_Arc_DireX0 = func_lengthArc(init_H,Rs,Rp,a_DireX,m_DireX,a_DireY,m_DireY)[0]
	length_Arc_DireY0 = func_lengthArc(init_H,Rs,Rp,a_DireX,m_DireX,a_DireY,m_DireY)[1]

	L_DireX0 = length_PQ_PlusX0 + length_PQ_MinusX0 + length_Arc_DireX0
	L_DireY0 = length_PQ_PlusY0 + length_PQ_MinusY0 + length_Arc_DireY0

	while(n_loop<=1e4 and epsilon_max<=epsilon_f):
		n_loop = n_loop+1
		Height = Height+step_H

		length_PQ_PlusX  = func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_DireX,m_DireX,a_DireY,m_DireY,Rs,Rp,Height)[0]
		length_PQ_MinusX = func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_DireX,m_DireX,a_DireY,m_DireY,Rs,Rp,Height)[1]
		length_PQ_PlusY  = func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_DireX,m_DireX,a_DireY,m_DireY,Rs,Rp,Height)[2]
		length_PQ_MinusY = func_lengthPQ(x1,y1,x2,y2,x3,y3,x4,y4,a_DireX,m_DireX,a_DireY,m_DireY,Rs,Rp,Height)[3]
		
		length_Arc_DireX = func_lengthArc(Height,Rs,Rp,a_DireX,m_DireX,a_DireY,m_DireY)[0]
		length_Arc_DireY = func_lengthArc(Height,Rs,Rp,a_DireX,m_DireX,a_DireY,m_DireY)[1]

		L_DireX = length_PQ_PlusX + length_PQ_MinusX + length_Arc_DireX
		L_DireY = length_PQ_PlusY + length_PQ_MinusY + length_Arc_DireY

		epsilon_X = (L_DireX-L_DireX0)/L_DireX0
		epsilon_Y = (L_DireY-L_DireY0)/L_DireY0

		epsilon_XY = np.concatenate((epsilon_X,epsilon_X,epsilon_Y,epsilon_Y),axis=0)
		epsilon_max = np.amax(epsilon_XY)
		print('It the',n_loop, 'th loop,','epsilon_XY=',epsilon_XY,'Height=',Height)


	sigma_XY = func_sigma(epsilon_XY, sigma_y, E1, E2)
	force_XY = sigma_XY * A_rope
	length_PQ = np.concatenate((length_PQ_PlusX,length_PQ_MinusX,length_PQ_PlusY,length_PQ_MinusY),axis=0)
	max_height = Height
	max_force = np.sum(force_XY*max_height/length_PQ)

	########################################################################
	# 本部分代码用于校准另一种方法
	w =  np.sqrt((x1-x2)**2+(y1-y2)**2)
	theta = np.arctan(y1/x1)
	Lu_PQ0 = func_cablenet_xyz(theta, init_H, w, Rp, Rs, a_DireY, m_DireY)[0]
	Lc_PQ0 = func_cablenet_xyz(theta, init_H, w, Rp, Rs, a_DireY, m_DireY)[1]
	Ld_PQ0 = func_cablenet_xyz(theta, init_H, w, Rp, Rs, a_DireY, m_DireY)[2]
	L_PQ0 = Lu_PQ0 + Lc_PQ0 + Ld_PQ0
	ED = np.linalg.norm((L_PQ0-L_DireY0),ord=2, axis=0, keepdims=False)
	if ED<1e-3:
		print('Test is passed')
	else:
		print('Test is failed')
	########################################################################

	print('max_height=',max_height)
	print('max_force=',max_force)
