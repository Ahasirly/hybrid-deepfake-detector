"""
Improved DistilDIRE model with ConvNeXt backbone
Based on Simple Baseline paper findings for Deepfake-Eval-2024
"""
import torch
import torch.nn as nn
import timm


class DistilDIREImproved(nn.Module):
    """
    Improved DistilDIRE using ConvNeXt-base backbone

    Key improvements over original ResNet-50:
    - Larger model (88M vs 38M parameters)
    - Larger receptive field (7x7 kernels vs 3x3)
    - Modern architecture with better inductive biases
    - CLIP pretraining on LAION-2B (much better than ImageNet for deepfakes)
    """

    def __init__(self, device, dropout=0.2, backbone='convnext_base', pretrained=True, use_clip=True):
        super().__init__()
        self.device = device

        # Load ConvNeXt backbone from timm
        # Use num_classes=0 to get feature extractor without classification head
        if use_clip and backbone == 'convnext_base':
            # Use CLIP-pretrained ConvNeXt from Hugging Face Hub
            # LAION-2B pretraining is much better for deepfake detection
            model_name = 'hf-hub:timm/convnext_base.clip_laion2b_augreg_ft_in1k'
            print(f"Loading CLIP-pretrained ConvNeXt from HF Hub: {model_name}")
            self.backbone = timm.create_model(
                model_name,
                pretrained=pretrained,
                num_classes=0,
                global_pool='avg'
            )
        else:
            # Use standard ImageNet-pretrained model
            self.backbone = timm.create_model(
                backbone,
                pretrained=pretrained,
                num_classes=0,
                global_pool='avg'
            )

        # Get feature dimension from backbone
        self.feature_dim = self.backbone.num_features

        # Dropout for regularization (critical for small datasets)
        self.dropout = nn.Dropout(dropout)

        # Binary classification head
        self.classifier = nn.Linear(self.feature_dim, 1)

        # Initialize classifier with small weights
        nn.init.normal_(self.classifier.weight, mean=0.0, std=0.01)
        nn.init.constant_(self.classifier.bias, 0.0)

    def forward(self, x, eps=None):
        """
        Forward pass - simplified to use only RGB images

        Args:
            x: Input images [B, 3, H, W]
            eps: Ignored for now (eps features not needed with stronger backbone)

        Returns:
            dict with 'logit' and 'feature' keys
        """
        # Extract features using ConvNeXt backbone
        features = self.backbone(x)

        # Apply dropout
        features_dropped = self.dropout(features)

        # Classification
        logit = self.classifier(features_dropped)

        return {
            'logit': logit,
            'feature': features  # Return features for potential KD loss
        }

    def get_feature_dim(self):
        """Return feature dimension for compatibility"""
        return self.feature_dim


class DistilDIREImprovedWithEPS(nn.Module):
    """
    Improved model with dual-stream architecture (RGB + EPS)
    Use this if single RGB stream doesn't achieve target performance
    """

    def __init__(self, device, dropout=0.2, backbone='convnext_base', pretrained=True):
        super().__init__()
        self.device = device

        # RGB stream
        self.rgb_backbone = timm.create_model(
            backbone,
            pretrained=pretrained,
            num_classes=0,
            global_pool='avg'
        )

        # EPS stream - smaller backbone
        self.eps_backbone = timm.create_model(
            'convnext_tiny',  # Use smaller model for EPS
            pretrained=pretrained,
            num_classes=0,
            global_pool='avg',
            in_chans=3  # EPS is also 3-channel
        )

        # Feature dimensions
        self.rgb_dim = self.rgb_backbone.num_features
        self.eps_dim = self.eps_backbone.num_features
        self.feature_dim = self.rgb_dim + self.eps_dim

        # Fusion and classification
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.feature_dim, 1)

        # Initialize
        nn.init.normal_(self.classifier.weight, mean=0.0, std=0.01)
        nn.init.constant_(self.classifier.bias, 0.0)

    def forward(self, x, eps):
        """
        Forward pass with both RGB and EPS

        Args:
            x: Input images [B, 3, H, W]
            eps: Diffusion noise [B, 3, H, W]

        Returns:
            dict with 'logit' and 'feature' keys
        """
        # Extract features from both streams
        rgb_features = self.rgb_backbone(x)
        eps_features = self.eps_backbone(eps)

        # Concatenate features
        features = torch.cat([rgb_features, eps_features], dim=1)

        # Apply dropout and classify
        features_dropped = self.dropout(features)
        logit = self.classifier(features_dropped)

        return {
            'logit': logit,
            'feature': features
        }
