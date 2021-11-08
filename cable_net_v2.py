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
def func_CN1_cablenet_test_xyz(theta, H, w, Rp, Rs, a, m):
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


def func_CN1_lengthArc(H,Rs,Rp,a_DireX,m_DireX,a_DireY,m_DireY):
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
	elif H <= 0.0:
		arc_length_DireX = 2*np.sqrt(Rp**2 - d_DireX**2)
		arc_length_DireY = 2*np.sqrt(Rp**2 - d_DireY**2)
	else:
		raise ValueError
	return arc_length_DireX,arc_length_DireY

def func_CN1_sigma(epsilon, sigma_y, E1, E2):
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

def func_CN1_loaded_xPyP(m1, d1, alpha1, Rp, H, ex, ey):
	i1_arr = np.arange(1,m1+0.1,step=1)  # 第一方向上与加载区域相交的钢丝绳序列（从1开始）

	yP1_plus_origin = d1/2*(2*i1_arr - m1 - 1)
	xP1_plus_origin = np.sqrt(Rp**2 - yP1_plus_origin**2)
	zP1_plus_origin = H*np.ones_like(yP1_plus_origin)

	yP1_minu_origin = yP1_plus_origin
	xP1_minu_origin = -xP1_plus_origin
	zP1_minu_origin = zP1_plus_origin

	xP1_plus = ex + xP1_plus_origin*np.cos(alpha1) - yP1_plus_origin*np.sin(alpha1)
	yP1_plus = ey + xP1_plus_origin*np.sin(alpha1) + yP1_plus_origin*np.cos(alpha1)
	zP1_plus = zP1_plus_origin

	xP1_minu = ex + xP1_minu_origin*np.cos(alpha1) - yP1_minu_origin*np.sin(alpha1)
	yP1_minu = ey + xP1_minu_origin*np.sin(alpha1) + yP1_minu_origin*np.cos(alpha1)
	zP1_minu = zP1_minu_origin

	return xP1_plus, yP1_plus, zP1_plus, xP1_minu, yP1_minu, zP1_minu

def func_CN1_solve_ABC(para_x1, para_y1, para_x2, para_y2):
	if np.min(abs(para_x2-para_x1))==0:
		A1_arr = np.ones_like(para_x1)
		B1_arr = np.zeros_like(para_x1)
		C1_arr = -para_x1+np.zeros_like(para_x1)
	else:
		A1_arr = (para_y2-para_y1)/(para_x2-para_x1)
		B1_arr = -1+np.zeros_like(A1_arr)
		C1_arr = para_y1-(para_y2-para_y1)/(para_x2-para_x1)*para_x1
	return A1_arr, B1_arr, C1_arr


def func_CN1_xy_intersection(A1, B1, C1, A2, B2, C2):
	if np.min(abs(A1*B2-A2*B1))==0:
		x_point = A1 + A2 + 10**100  # 采用大数淹没，避免除0报警
		y_point = A1 + A2 + 10**100  # 采用大数淹没，避免除0报警
	else:
		x_point =  (B1*C2-B2*C1)/(A1*B2-A2*B1)
		y_point =  (A2*C1-A1*C2)/(A1*B2-A2*B1)
	return x_point, y_point


# 本函数用于删除钢丝绳网与锚固点之间边界线延长线上的交点
def func_CN1_pick_xQyQ(m1, xQ_line12, yQ_line12, xQ_line23, yQ_line23, xQ_line34, yQ_line34, xQ_line41, yQ_line41, x1, y1, x2, y2, x3, y3, x4, y4):
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
			yQ1[i1] = yQ_line12[i12]
			i1 = i1 + 1
	for i23 in range(len(xQ_line23)):
		if xQ_line23[i23]<x2 and xQ_line23[i23]<x3:
			pass
		elif  xQ_line23[i23]>x2 and xQ_line23[i23]>x3:
			pass
		else:
			xQ1[i1] = xQ_line23[i23]
			yQ1[i1] = yQ_line23[i23]
			i1 = i1 + 1
	for i34 in range(len(xQ_line34)):
		if xQ_line34[i34]<x3 and xQ_line34[i34]<x4:
			pass
		elif  xQ_line34[i34]>x3 and xQ_line34[i34]>x4:
			pass
		else:
			xQ1[i1] = xQ_line34[i34]				
			yQ1[i1] = yQ_line34[i34]	
			i1 = i1 + 1
	for i41 in range(len(xQ_line41)):
		if xQ_line41[i41]<x1 and xQ_line41[i41]<x4:
			pass
		elif  xQ_line41[i41]>x1 and xQ_line41[i41]>x4:
			pass
		else:
			xQ1[i1] = xQ_line41[i41]
			yQ1[i1] = yQ_line41[i41]
			i1 = i1 + 1
	return xQ1, yQ1


def func_CN1_sort_xQyQ(m1, xQ1, yQ1, xP1_plus, yP1_plus, xP1_minu, yP1_minu):
	xQ1_plus = np.zeros(m1)
	yQ1_plus = np.zeros(m1)
	yQ1_minu = np.zeros(m1)
	xQ1_minu = np.zeros(m1)

	for i in range(len(xP1_plus)):
		if abs(xP1_plus[i] - xP1_minu[i]) < 1e-16:
			for j in range(len(xQ1)):
				if abs(xQ1[j] - xP1_plus[i]) < 1e-16:
					if (yQ1[j] - yP1_plus[i])>1e-16:
						xQ1_plus[i] = xQ1[j]
						yQ1_plus[i] = yQ1[j]
					elif (yQ1[j] - yP1_plus[i])<-1e-16:  # python对于数值的绝对相等判别存在非常非常小1e-16但是不可忽略的误差
						xQ1_minu[i] = xQ1[j]
						yQ1_minu[i] = yQ1[j]
					else:
						raise ValueError
				else:
					pass
		else:
			for j in range(len(xQ1)):
				k_search = (yQ1[j] - yP1_plus[i])/(xQ1[j] - xP1_plus[i])
				k_target = (yP1_plus[i] - yP1_minu[i])/(xP1_plus[i] - xP1_minu[i])
				if abs(k_search-k_target) < 1e-16:
					if (yQ1[j] - yP1_plus[i])>1e-16:
						xQ1_plus[i] = xQ1[j]
						yQ1_plus[i] = yQ1[j]
					elif (yQ1[j] - yP1_plus[i])<-1e-16:  # python对于数值的绝对相等判别存在非常非常小1e-16但是不可忽略的误差
						xQ1_minu[i] = xQ1[j]
						yQ1_minu[i] = yQ1[j]
					elif abs(yQ1[j] - yP1_plus[i]) < 1e-16:
						#print('i=',i, 'xQ1[j]=',xQ1[j],'yQ1[j]=',yQ1[j])
						if xQ1[j] > xP1_plus[i]:
							xQ1_plus[i] = xQ1[j]
							yQ1_plus[i] = yQ1[j]
						elif xQ1[j] < xP1_plus[i]:
							xQ1_minu[i] = xQ1[j]
							yQ1_minu[i] = yQ1[j]
						else:
							raise ValueError
					else:
						raise ValueError	
				else:
					pass
	return xQ1_plus, yQ1_plus, xQ1_minu, yQ1_minu

# 参数输入----------------------------------------------------------------------------------- #
if __name__ == '__main__':

	d1, d2 = 0.3, 0.3  # 本程序可以用于计算两侧不同的a值（网孔间距）
	alpha1, alpha2 = np.pi/6, np.pi/2  # 钢丝绳方向角，取值范围为半闭半开区间[0,pi)

	ex, ey = 0, 0
	Rs = 1.2  # 球罐形加载顶头半径
	Rp = 0.5  # 加载顶头水平投影半径，若加载形状为多边形时考虑为半径为Rp圆内切

	n_loop = 0 # 初始增量步数
	epsilon_max = 0.0  # 钢丝绳初始应变
	epsilon_f = 0.0235  # 钢丝绳失效应变
	init_H = 0.55  # 钢丝绳网在重力作用下初始垂度（初始高度)

	m1 = 2*func_round(Rp/d1)  # 第1方向上与加载区域相交的钢丝绳数量（偶数）
	m2 = 2*func_round(Rp/d2)  # 第2方向上与加载区域相交的钢丝绳数量（偶数）

	#x1, y1 = 1.5*np.sqrt(2), 0
	#x2, y2 = 0, 1.5*np.sqrt(2)
	#x3, y3 = -1.5*np.sqrt(2), 0
	#x4, y4 = 0, -1.5*np.sqrt(2)

	x1, y1 = 1.5, -1.5
	x2, y2 = 1.5, 1.5
	x3, y3 = -1.5, 1.5
	x4, y4 = -1.5, -1.5

	E1, E2 = 91.304e9, 25.0e9
	sigma_y = 1050e6
	sigma_f = 1350e6
	fail_force = 40700
	A_rope = fail_force/sigma_f


	# 初始时刻加载区域边缘力的作用点（P点）坐标，方向1与方向2，P点坐标随着加载位移的变换实时变化
	xP1_plus, yP1_plus, zP1_plus, xP1_minu, yP1_minu, zP1_minu = func_CN1_loaded_xPyP(m1, d1, alpha1, Rp, init_H, ex, ey)
	xP2_plus, yP2_plus, zP2_plus, xP2_minu, yP2_minu, zP2_minu = func_CN1_loaded_xPyP(m2, d2, alpha2, Rp, init_H, ex, ey)


	# 求解计算过程中钢丝绳网片边界上力的作用点（Q点）坐标，方向1与方向2，Q点坐标不随加载位移的变换改变
	A1_arr, B1_arr, C1_arr = func_CN1_solve_ABC(xP1_minu, yP1_minu, xP1_plus, yP1_plus)  # 与加载区域边缘相交的1方向的钢丝绳直线方程系数A1x+B1y+C1=0
	A2_arr, B2_arr, C2_arr = func_CN1_solve_ABC(xP2_minu, yP2_minu, xP2_plus, yP2_plus)  # 与加载区域边缘相交的2方向的钢丝绳直线方程系数A2x+B2y+C2=0

	A_line12, B_line12, C_line12 = func_CN1_solve_ABC(x1, y1, x2, y2)  # 边界线方程（锚点之间的连接线）A_linex+B_liney+C_line=0
	A_line23, B_line23, C_line23 = func_CN1_solve_ABC(x2, y2, x3, y3)
	A_line34, B_line34, C_line34 = func_CN1_solve_ABC(x3, y3, x4, y4)
	A_line41, B_line41, C_line41 = func_CN1_solve_ABC(x4, y4, x1, y1)

	xQ1_line12, yQ1_line12 = func_CN1_xy_intersection(A1_arr, B1_arr, C1_arr, A_line12, B_line12, C_line12)  # 钢丝绳直线束与边界线（锚点1与锚点2连线）的交点，方向1
	xQ1_line23, yQ1_line23 = func_CN1_xy_intersection(A1_arr, B1_arr, C1_arr, A_line23, B_line23, C_line23)  # 钢丝绳直线束与边界线（锚点2与锚点3连线）的交点，方向1
	xQ1_line34, yQ1_line34 = func_CN1_xy_intersection(A1_arr, B1_arr, C1_arr, A_line34, B_line34, C_line34)  # 钢丝绳直线束与边界线（锚点3与锚点4连线）的交点，方向1
	xQ1_line41, yQ1_line41 = func_CN1_xy_intersection(A1_arr, B1_arr, C1_arr, A_line41, B_line41, C_line41)  # 钢丝绳直线束与边界线（锚点4与锚点1连线）的交点，方向1

	xQ2_line12, yQ2_line12 = func_CN1_xy_intersection(A2_arr, B2_arr, C2_arr, A_line12, B_line12, C_line12)  # 钢丝绳直线束与边界线（锚点1与锚点2连线）的交点，方向2
	xQ2_line23, yQ2_line23 = func_CN1_xy_intersection(A2_arr, B2_arr, C2_arr, A_line23, B_line23, C_line23)  # 钢丝绳直线束与边界线（锚点2与锚点3连线）的交点，方向2
	xQ2_line34, yQ2_line34 = func_CN1_xy_intersection(A2_arr, B2_arr, C2_arr, A_line34, B_line34, C_line34)  # 钢丝绳直线束与边界线（锚点3与锚点4连线）的交点，方向2
	xQ2_line41, yQ2_line41 = func_CN1_xy_intersection(A2_arr, B2_arr, C2_arr, A_line41, B_line41, C_line41)  # 钢丝绳直线束与边界线（锚点4与锚点1连线）的交点，方向2

	xQ1_pick, yQ1_pick = func_CN1_pick_xQyQ(m1, xQ1_line12, yQ1_line12, xQ1_line23, yQ1_line23, xQ1_line34, yQ1_line34, xQ1_line41, yQ1_line41, x1, y1, x2, y2, x3, y3, x4, y4)  # 挑选出边界线段范围内的交点，方向1
	xQ2_pick, yQ2_pick = func_CN1_pick_xQyQ(m2, xQ2_line12, yQ2_line12, xQ2_line23, yQ2_line23, xQ2_line34, yQ2_line34, xQ2_line41, yQ2_line41, x1, y1, x2, y2, x3, y3, x4, y4)  # 挑选出边界线段范围内的交点，方向2

	xQ1_plus, yQ1_plus, xQ1_minu, yQ1_minu = func_CN1_sort_xQyQ(m1, xQ1_pick, yQ1_pick, xP1_plus, yP1_plus, xP1_minu, yP1_minu)  # 对挑选出来的交点进行重新排序，使得边界线上的交点与加载边缘上的交点一一对应，与实际钢丝绳网中匹配关系一致，方向1
	xQ2_plus, yQ2_plus, xQ2_minu, yQ2_minu = func_CN1_sort_xQyQ(m2, xQ2_pick, yQ2_pick, xP2_plus, yP2_plus, xP2_minu, yP2_minu)  # 对挑选出来的交点进行重新排序，使得边界线上的交点与加载边缘上的交点一一对应，与实际钢丝绳网中匹配关系一致，方向2
	zQ1_plus, zQ1_minu = np.zeros_like(xQ1_plus), np.zeros_like(xQ1_plus)
	zQ2_plus, zQ2_minu = np.zeros_like(xQ2_plus), np.zeros_like(xQ2_plus)



	print('xQ2_plus=',xQ2_plus)
	print('yQ2_plus=',yQ2_plus)
	print('xQ2_minu=',xQ2_minu)
	print('yQ2_minu=',yQ2_minu)







	length_PQ1_plus = np.sqrt((xP1_plus-xQ1_plus)**2+(yP1_plus-yQ1_plus)**2+(zP1_plus-zQ1_plus)**2)
	length_PQ1_minu = np.sqrt((xP1_minu-xQ1_minu)**2+(yP1_minu-yQ1_minu)**2+(zP1_minu-zQ1_minu)**2)

	length_PQ2_plus = np.sqrt((xP2_plus-xQ2_plus)**2+(yP2_plus-yQ2_plus)**2+(zP2_plus-zQ2_plus)**2)
	length_PQ2_minu = np.sqrt((xP2_minu-xQ2_minu)**2+(yP2_minu-yQ2_minu)**2+(zP2_minu-zQ2_minu)**2)





	length_Arc1 = func_CN1_lengthArc(init_H,Rs,Rp,d1,m1,d2,m2)[0]
	length_Arc2 = func_CN1_lengthArc(init_H,Rs,Rp,d1,m1,d2,m2)[1]

	L0_Dire1 = length_PQ1_plus + length_PQ1_minu + length_Arc1
	L0_Dire2 = length_PQ2_plus + length_PQ2_minu + length_Arc2
	print('L0_Dire1=',L0_Dire1)
	print('L0_Dire2=',L0_Dire2)

	Height = 0.0  # 网片加载位移
	step_H = 1e-4  # 网片位移加载增量步长，单位：m

	while(n_loop<=1e4 and epsilon_max<=epsilon_f):

		xP1_plus, yP1_plus, zP1_plus, xP1_minu, yP1_minu, zP1_minu = func_CN1_loaded_xPyP(m1, d1, alpha1, Rp, Height, ex, ey)
		xP2_plus, yP2_plus, zP2_plus, xP2_minu, yP2_minu, zP2_minu = func_CN1_loaded_xPyP(m2, d2, alpha2, Rp, Height, ex, ey)

		length_PQ1_plus = np.sqrt((xP1_plus-xQ1_plus)**2+(yP1_plus-yQ1_plus)**2+(zP1_plus-zQ1_plus)**2)
		length_PQ1_minu = np.sqrt((xP1_minu-xQ1_minu)**2+(yP1_minu-yQ1_minu)**2+(zP1_minu-zQ1_minu)**2)
		
		length_PQ2_plus = np.sqrt((xP2_plus-xQ2_plus)**2+(yP2_plus-yQ2_plus)**2+(zP2_plus-zQ2_plus)**2)
		length_PQ2_minu = np.sqrt((xP2_minu-xQ2_minu)**2+(yP2_minu-yQ2_minu)**2+(zP2_minu-zQ2_minu)**2)

		length_Arc1 = func_CN1_lengthArc(Height,Rs,Rp,d1,m1,d2,m2)[0]
		length_Arc2 = func_CN1_lengthArc(Height,Rs,Rp,d1,m1,d2,m2)[1]

		L_Dire1 = length_PQ1_plus + length_PQ1_minu + length_Arc1
		L_Dire2 = length_PQ2_plus + length_PQ2_minu + length_Arc2

		epsilon1 = (L_Dire1-L0_Dire1)/L0_Dire1
		epsilon2 = (L_Dire2-L0_Dire2)/L0_Dire2
		epsilon_all = np.concatenate((epsilon1,epsilon2),axis=0)
		epsilon_max = np.amax(epsilon_all)

		n_loop = n_loop+1
		Height = Height+step_H

		print('It the',n_loop, 'th loop,','epsilon_max=',epsilon_max,'Height=',Height)


	sigma_XY = func_CN1_sigma(epsilon_XY, sigma_y, E1, E2)
	force_XY = sigma_XY * A_rope
	length_PQ = np.concatenate((length_PQ_plusX,length_PQ_minusX,length_PQ_plusY,length_PQ_minusY),axis=0)
	max_height = Height
	max_force = np.sum(force_XY*max_height/length_PQ)

	########################################################################
	# 本部分代码用于校准另一种方法
	w =  np.sqrt((x1-x2)**2+(y1-y2)**2)
	theta = np.arctan(y1/x1)
	Lu_PQ0 = func_CN1_cablenet_xyz(theta, init_H, w, Rp, Rs, a_DireY, m_DireY)[0]
	Lc_PQ0 = func_CN1_cablenet_xyz(theta, init_H, w, Rp, Rs, a_DireY, m_DireY)[1]
	Ld_PQ0 = func_CN1_cablenet_xyz(theta, init_H, w, Rp, Rs, a_DireY, m_DireY)[2]
	L_PQ0 = Lu_PQ0 + Lc_PQ0 + Ld_PQ0
	ED = np.linalg.norm((L_PQ0-L_DireY0),ord=2, axis=0, keepdims=False)
	if ED<1e-3:
		print('Test is passed')
	else:
		print('Test is failed')
	########################################################################

	print('max_height=',max_height)
	print('max_force=',max_force)
