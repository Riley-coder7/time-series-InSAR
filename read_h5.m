function [data,Name] = read_h5(H5FILE,epoch);
% READ_H5  -- Read binary data of h5 file.
%
%     data = read_h5(H5FILE,epoch)
%
%     data  : output binary data
%     H5FILE: input h5file
%     epoch : for timeseries H5FILE, input epoch to read, default: epoch = 1
%
%  Author:  Yunmeng Cao
%  E-mail:  ymcmrs@gmail.com
%  Date  :  26, Oct. 2017
%

if nargin==0, help read_h5; end
if nargin<2, epoch=1;end



info = hdf5info(H5FILE);

% calculate group number 
N_group = length(info.GroupHierarchy.Groups);
N_data = length(info.GroupHierarchy.Groups(1).Datasets);


if N_group ==1 && N_data ==1
    STR = 'single_data';
elseif N_group==1 && N_data~=1
    STR = 'timeseries_data';
elseif N_group~=1 && N_data==1
    STR = 'multi_group_data';
end

STR

if strcmpi(STR,'single_data')
    data = hdf5read(info.GroupHierarchy.Groups(1).Datasets(1));
    Name = info.GroupHierarchy.Groups(1).Datasets(1).Name;
elseif strcmpi(STR,'timeseries_data')
    data = hdf5read(info.GroupHierarchy.Groups(1).Datasets(epoch));
    Name = info.GroupHierarchy.Groups(1).Datasets(epoch).Name;
elseif strcmpi(STR,'multi_group_data')
    data = hdf5read(info.GroupHierarchy.Groups(epoch).Datasets(1));
    Name = info.GroupHierarchy.Groups(epoch).Datasets(1).Name;
end
data = data';

end

