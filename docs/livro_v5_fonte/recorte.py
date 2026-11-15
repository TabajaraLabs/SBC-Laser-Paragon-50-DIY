import cv2, numpy as np
src='/mnt/user-data/uploads/Claude/Paragon50/Fotos do laser original/3.jpg'
full=cv2.imread(src); fh,fw=full.shape[:2]
sm=cv2.resize(full,(600,800))
poly=np.array([(155,0),(306,0),(306,405),(380,418),(462,462),(450,520),(432,545),(432,730),(446,750),(446,775),(412,792),(250,792),(165,790),(138,722),(188,735),(186,500),(158,475),(154,420)],np.int32)
M=np.zeros((800,600),np.uint8); cv2.fillPoly(M,[poly],1)
k=lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
sure=cv2.erode(M,k(14)); prob=cv2.dilate(M,k(10))
mask=np.full((800,600),cv2.GC_BGD,np.uint8)
mask[prob>0]=cv2.GC_PR_BGD; mask[M>0]=cv2.GC_PR_FGD; mask[sure>0]=cv2.GC_FGD
bg=np.zeros((1,65)); fg=np.zeros((1,65))
cv2.grabCut(sm,mask,None,bg,fg,10,cv2.GC_INIT_WITH_MASK)
m=((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD)).astype(np.uint8)
# limpa: maior componente + fecha buracos
n,lab,st,_=cv2.connectedComponentsWithStats(m); 
if n>1: m=(lab==1+np.argmax(st[1:,4])).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,k(5)); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,k(2))
m[:432,:164]=0; m[262:432,:174]=0; g=cv2.cvtColor(sm,cv2.COLOR_BGR2GRAY); box=np.zeros_like(m); box[420:482,424:470]=1; m[(box>0)&(g<95)]=0; m[:14,205:300]=0
cv2.imwrite('pg/mask3.png',m*255)
prev=sm.copy(); prev[m==0]=(255,255,255); cv2.imwrite('pg/prev3.png',prev)
mf=cv2.resize(m*255,(fw,fh),interpolation=cv2.INTER_CUBIC); mf=cv2.GaussianBlur(mf,(0,0),2.2)
rgba=cv2.cvtColor(full,cv2.COLOR_BGR2BGRA); rgba[:,:,3]=mf
ys,xs=np.where(mf>20); rgba=rgba[ys.min():ys.max()+1,xs.min():xs.max()+1]
h=rgba.shape[0]
a=rgba[:,:,3].astype(np.float32)
ramp=np.clip(np.arange(h)/200.0,0,1)[:,None]; a=a*ramp
rgba[:,:,3]=a.astype(np.uint8)
cv2.imwrite('img/laser_recorte.png',rgba); print(rgba.shape)
