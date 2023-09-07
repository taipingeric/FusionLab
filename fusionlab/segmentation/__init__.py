from fusionlab import BACKEND
if BACKEND['torch']:
    from .unet.unet import UNet
    from .resunet.resunet import ResUNet
    from .unet2plus.unet2plus import UNet2plus
    from .transunet.transunet import TransUNet
    from .unetr.unetr import UNETR
    from .segformer.segformer import SegFormer
    from .base import HFSegmentationModel
if BACKEND['tf']:
    from .unet.tfunet import TFUNet
    from .resunet.tfresunet import TFResUNet
    from .unet2plus.tfunet2plus import TFUNet2plus