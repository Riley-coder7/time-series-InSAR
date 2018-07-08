function Sigma_Phase=CohMLooks(Gamma,L);

% ****************************************************************
% CohMLooks -- Script to calculate standard deviation of interferometric phase based on Coherence and Multilook number
%
%
%   Gamma     : 1-D coherence vector, eg. [0.7,0.7,0.6,0.5,0.8,0.4,0.5,...],both for a line or a column 
%     L       : Multilooks number
%  Sigma_Phase: The vector of phase standard deviation, the same size as Gamma
%
%
%  Author: YunMeng Cao  
%                           2014-11-19
%**********************************************************


[row,col]=size(Gamma);
N=length(Gamma);
Sigma_Phase=zeros(N,1);
Li=zeros(row,col);
phai=-pi:pi/1000:pi;


if L==1
        for t=1:1000
            Li=Li+(Gamma.^(2*t))/(t^2);  
          end
      Sigma_Phase=sqrt((pi^2)/3-pi*asin(Gamma)+(asin(Gamma)).^2-Li/2);
else

    for i=1:N


    belta=Gamma(i)*cos(phai);
     F1=((1-Gamma(i)^2)^L)/(2*pi);
     F2=(gamma(2*L-1))/(((gamma(L))^2)*(2^(2*(L-1))));
     F3=(2*L-1)*belta./((1-belta.^2).^(L+0.5)).*(pi/2+asin(belta))+1./((1-belta.^2).^L);
    SUM=zeros(1,2001);
         for h=0:L-2
           SUM=SUM+(gamma(L-0.5))/(gamma(L-0.5-h))*(gamma(L-1-h))/(gamma(L-1))*(1+(1+2*h)*(belta.^2))./((1-belta.^2).^(h+2));
         end
      
           F4=1/(2*(L-1))*SUM;
           pdf2=F1*(F2*F3+F4);
           SPDF=pdf2.*(phai.^2)*pi/1000;
          Sigma_Phase(i)=sqrt(sum(SPDF(:)));
    end
end
         
          



