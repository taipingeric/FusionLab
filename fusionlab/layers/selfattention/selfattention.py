import torch
import torch.nn as nn
from fusionlab.layers import Rearrange


class SelfAttention(nn.Module):
    """
    A self-attention block, based on: "Dosovitskiy et al.,
    An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale <https://arxiv.org/abs/2010.11929>"

    source code: https://github.com/Project-MONAI/MONAI/blob/main/monai/networks/blocks/selfattention.py#L22
    """

    def __init__(
        self,
        hidden_size: int,
        num_heads: int,
        dropout_rate: float = 0.0,
        qkv_bias: bool = False,
        save_attn: bool = False,
    ) -> None:
        """
        Args:
            hidden_size (int): dimension of hidden layer.
            num_heads (int): number of attention heads.
            dropout_rate (float, optional): faction of the input units to drop. Defaults to 0.0.
            qkv_bias (bool, optional): bias term for the qkv linear layer. Defaults to False.
            save_attn (bool, optional): to make accessible the attention matrix. Defaults to False.

        """

        super().__init__()

        if not (0 <= dropout_rate <= 1):
            raise ValueError("dropout_rate should be between 0 and 1.")

        if hidden_size % num_heads != 0:
            raise ValueError("hidden size should be divisible by num_heads.")

        self.num_heads = num_heads
        self.out_proj = nn.Linear(hidden_size, hidden_size)
        self.qkv = nn.Linear(hidden_size, hidden_size * 3, bias=qkv_bias)
        # b: batch size, h: num_patches, l: num_heads, d: head_dim
        self.input_rearrange = Rearrange("b h (qkv l d) -> qkv b l h d", qkv=3, l=num_heads)
        self.out_rearrange = Rearrange("b h l d -> b l (h d)")
        self.drop_output = nn.Dropout(dropout_rate)
        self.drop_weights = nn.Dropout(dropout_rate)
        self.head_dim = hidden_size // num_heads
        self.scale = self.head_dim**-0.5
        self.save_attn = save_attn
        self.att_mat = torch.Tensor()

    def forward(self, x):
        qkv = self.input_rearrange(self.qkv(x))
        q, k, v = qkv[0], qkv[1], qkv[2] # (b, l, h, d)
        att_mat = (torch.einsum("blxd,blyd->blxy", q, k) * self.scale).softmax(dim=-1) # (b, l, h, h)
        if self.save_attn:
            self.att_mat = att_mat.detach()

        att_mat = self.drop_weights(att_mat)
        x = torch.einsum("bhxy,bhyd->bhxd", att_mat, v) # (b, l, h, d)
        x = self.out_rearrange(x)
        x = self.out_proj(x)
        x = self.drop_output(x)
        return x