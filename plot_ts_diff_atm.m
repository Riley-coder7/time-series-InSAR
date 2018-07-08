function plot_ts_diff_atm(FILE1,FILE2);



    function F = myfun(a,xdata)
        F = a(1)+a(2)*sin(2*pi*(xdata+a(3)))+a(4)*xdata;
    end


%[a1,a2,a3,a4,a5,a6,a7,a8]=textread('EBRG_TS_Trop','%s%s%f%f%f%f%f%f');
[a1,a20,a21,a22,a3,a4,a5,a6,a7,a8]=textread(FILE1,'%s%f:%f:%f%f%f%f%f%f%f');
[b1,b20,b21,b22,b3,b4,b5,b6,b7,b8]=textread(FILE2,'%s%f:%f:%f%f%f%f%f%f%f');

taa=a20*365+a21;
tbb=b20*365+b21;

[vv,faa,fbb]=intersect(taa,tbb);



ta0 = 2000+a20+a21/365;

ttt = ta0(faa);
yaa = a3(faa);
ybb=b3(fbb);
dy = yaa - ybb;

figure(100);clf;

GPS1=a1{1};UTC0=a22(1)/3600;UTC=strcat(num2str(UTC0),':00 ','  UTC');
GPS2=b1{1};
a0 = [0,10,0,0];
[aa,resnorm,residual] = lsqcurvefit(@myfun,a0,ttt,dy/10);


TT = ttt;
TT0 =min(TT):0.001:max(TT);
YY0 =  aa(1)+aa(2)*sin(2*pi*(TT0+aa(3)))+aa(4)*TT0;

YY1 =  aa(1)+aa(2)*sin(2*pi*(TT+aa(3)))+aa(4)*TT;
MM=corrcoef(YY1,dy/10);CC=MM(2,1);
P = round(aa(2)*100)/100;
Slope = round(aa(4)*100)/100;
CC = round(CC*100)/100;


a3 = dy;
dly = max(dy)-min(dy)+0.2*max(max(dy)-min(dy));
dly=dly/10;
plot(TT,dy/10,'bo-');hold on;
plot(TT0,YY0,'r-','linewidth',2);

%title(strcat(GPS,UTC));

text(min(TT)+0.1/3*(max(TT)-min(TT)),min(dy/10)-0.1*dly+2.9/3*dly,strcat('station:',GPS1,'-',GPS2),'fontname','Times New Roman','fontweight','bold','fontsize',20);
text(min(TT)+2.5/3*(max(TT)-min(TT)),min(dy/10)-0.1*dly+2.9/3*dly,UTC,'fontname','Times New Roman','fontweight','bold','fontsize',20);

PP = strcat('Amplitude: ', num2str(abs(P)),' cm');
SS = strcat('Slope        : ', '  ',num2str(Slope),' cm/year');
CC00 = strcat('R : ', '  ',num2str(CC));

text(min(TT)+0.1/3*(max(TT)-min(TT)),min(a3/10)+0.2/3*((max(a3/10)-min(a3/10))),PP,'fontname','Times New Roman','fontsize',16);
text(min(TT)+0.1/3*(max(TT)-min(TT)),min(a3/10)+0/3*((max(a3/10)-min(a3/10))),SS,'fontname','Times New Roman','fontsize',16);
text(min(TT)+0.7/3*(max(TT)-min(TT)),min(a3/10)+0/3*((max(a3/10)-min(a3/10))),CC00,'fontname','Times New Roman','fontsize',16);

set(gcf,'unit','centimeters','position',[15 15 40 15]);
ylabel('Zenith Tropospheric Delay (cm)','fontweight','bold');
xlabel('Time (Year)','fontweight','bold');
set(gca,'Position',[.08 .15 .87 .8],'fontsize',18,'fontname','Times New Roman','linewidth',1);grid on;
dy=dy/10;
xlim([min(TT),max(TT)]); ylim([min(dy)-0.1*(max(dy)-min(dy)),max(dy)+0.1*(max(dy)-min(dy))])
dly = max(dy)-min(dy)+0.2*max(max(dy)-min(dy));


end