import torch
import torch.nn as nn

# Bottleneck sequence of layers used for creating resnet architecture
class Bottleneck(nn.Module):
    expansion = 4

    def __init__( self, in_channels, out_channels, stride = 1, downsample = None ):
        super(Bottleneck, self).__init__()
        
        # Define all layers and layer names
        self.conv1 = nn.Conv2d( in_channels, out_channels, kernel_size = 1, bias = False )
        self.bn1 = nn.BatchNorm2d(out_channels)
        
        self.conv2 = nn.Conv2d( out_channels, out_channels, kernel_size = 3, stride = stride, padding = 1, bias = False )
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.conv3 = nn.Conv2d( out_channels, 4*out_channels, kernel_size = 1, bias = False )
        self.bn3 = nn.BatchNorm2d( 4*out_channels )
        
        self.relu = nn.ReLU( inplace = True )
        
        self.downsample = downsample
        self.stride = stride
     
    # Forward pass of the bottleneck sequence
    def forward(self, x):
        residual = x
        out = nn.Sequential( self.conv1, self.bn1, self.relu, self.conv2, self.bn2, self.relu, self.conv3, self.bn3 ) (x)
        
        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out

# Class of Resnet architecture
class ResNet(nn.Module):
    def __init__( self, block, layers, num_classes = 1000 ):
        self.in_channels = 128
        super(ResNet, self).__init__()
        
        self.conv1 = nn.Conv2d( 3, 64, kernel_size = 3, stride = 2, padding = 1, bias = False )
        self.bn1   = nn.BatchNorm2d(64)
        self.relu1 = nn.ReLU(inplace = True)
        
        self.conv2 = nn.Conv2d( 64, 64, kernel_size = 3, stride = 1, padding = 1, bias = False )
        self.bn2   = nn.BatchNorm2d(64)
        self.relu2 = nn.ReLU(inplace = True)
        
        self.conv3 = nn.Conv2d( 64, 128, kernel_size = 3, stride = 1, padding = 1, bias = False )
        self.bn3   = nn.BatchNorm2d(128)
        self.relu3 = nn.ReLU( inplace = True )
        self.maxpool = nn.MaxPool2d( kernel_size = 3, stride = 2, padding = 1 )

        self.layer1 = self._make_layer( block, 64 , layers[0] )
        self.layer2 = self._make_layer( block, 128, layers[1], stride = 2 )
        self.layer3 = self._make_layer( block, 256, layers[2], stride = 2 )
        self.layer4 = self._make_layer( block, 512, layers[3], stride = 2 )
        
        self.avgpool = nn.AvgPool2d( 7, stride = 1 )
        self.fc = nn.Linear( 512*block.expansion, num_classes )
        
        # Initialize weights (Initialize Conv layers using Xavier initialization)
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, (2. / n)**0.5 )
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()
    
    # Method for creating sequential layer with bottleneck sequence layer
    def _make_layer( self, block, out_channels, blocks, stride = 1 ):
        downsample = None
        if stride != 1 or self.in_channels != out_channels*block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d( self.in_channels, out_channels*block.expansion, kernel_size = 1, stride = stride, bias = False ),
                nn.BatchNorm2d( out_channels*block.expansion )
            )

        layers = []
        layers.append(block(self.in_channels, out_channels, stride, downsample))
        self.in_channels = out_channels * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.in_channels, out_channels))

        return nn.Sequential(*layers)
    
    # Forward pass of the network
    def forward(self, x):        
        x = nn.Sequential(
            self.conv1, self.bn1, self.relu1,
            self.conv2, self.bn2, self.relu2,
            self.conv3, self.bn3, self.relu3, 
            self.maxpool,
            self.layer1, self.layer2, self.layer3, self.layer4,
            self.avgpool
        )
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        
        return x
    
# Instantiate resnet50 with specific number of layers and load pretrained network if needed
def resnet50( pretrained = False ):
    model = ResNet( Bottleneck, [3,4,6,3] )
    
    # Loading pretrained resnet50
    if pretrained:
        model.load_state_dict( torch.load( 'Model weights/resnet50-imagenet.pth', map_location=lambda storage, loc: storage ),
                               strict = False )        
    return model