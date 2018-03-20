%%
% Data Testing Space for Mouse Vital Monitoring 


load('ExampleData.mat')

time_raw = data(:,1);
volts = data(:,2);

time = linspace(0, 16.24, length(time_raw));

figure;
plot(time, volts)
xlabel('Time (min)')
ylabel('Volts')

minute = volts(1:60000);

time_min = linspace(0, 1, length(minute));

figure;
plot(time_min, minute)

lpFilt = designfilt('lowpassiir','FilterOrder',8, 'PassbandFrequency',2,'PassbandRipple',0.2,'SampleRate',200e3);

hpFilt = designfilt('highpassiir','FilterOrder',8, 'PassbandFrequency',3,'PassbandRipple',0.2,'SampleRate',200e3);
     
bpFilt = designfilt('bandpassiir','FilterOrder',20, 'HalfPowerFrequency1',0.5,'HalfPowerFrequency2',10,'SampleRate',1500);

HR = filter(hpFilt, minute);
breathing = filter(lpFilt, minute);
both = filter(bpFilt, minute);

figure;
plot(time_min, both)

figure;
plot(time_min, breathing)

figure;
plot(time_min, HR)


[pks, loc] =  findpeaks(HR, 'MinPeakDistance', 1000);


for i = 2:length(loc)
    
    dist(i) = loc(i)/6000 - loc(i-1)/6000;
    
end

breathing_rate = 1./dist;


%%

Fs = 1000;                      % samples per second
dt = 1/Fs;                     % seconds per sample
StopTime = 60;                  % seconds
t = (0:dt:StopTime-dt)';
N = size(t,1);
  
%Sine wave:


% Fourier Transform:
X = fftshift(fft(minute));
   
% Frequency specifications:
dF = Fs/N;                      % hertz
f = -Fs/2:dF:Fs/2-dF;           % hertz
   
% Plot the spectrum:
figure;
plot(f,abs(X)/N);
xlabel('Frequency (in hertz)');
title('Magnitude Response');

