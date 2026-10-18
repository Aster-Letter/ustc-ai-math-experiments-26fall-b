"""分阶段自检；未完成骨架应给出明确失败，不能当作通过。"""
import argparse
import torch
from PIL import Image
import numpy as np
from torch.nn import functional as F
import operator_exercises as student
from data import convert_trimap
from metrics import masked_loss, foreground_scores
from models import build_model
from student_encoder import PetEncoder, ImprovedEncoder


def check_operators():
    """用不同输入核对卷积、激活和池化。"""
    image = torch.arange(1, 10, dtype=torch.float32).reshape(3, 3)
    kernel = torch.tensor([[1., 0.], [0., -1.]])
    expected = torch.full((2, 2), -4.)
    assert torch.allclose(student.correlate2d(image, kernel), expected), "T2.1: expected all -4"
    image = torch.arange(20, dtype=torch.float32).reshape(4, 5)
    kernel = torch.tensor([[1., -2., 3.], [0., 1., -1.]])
    expected = F.conv2d(image[None, None], kernel[None, None])[0, 0]
    assert torch.allclose(student.correlate2d(image, kernel), expected), "T2.1: rectangular kernel"
    x = torch.tensor([[-2., 1.], [0., 3.]])
    assert torch.equal(student.relu(x), torch.tensor([[0., 1.], [0., 3.]])), "T2.2: negative values"
    expected = F.max_pool2d(image[None, None], 2)[0, 0]
    assert torch.equal(student.max_pool2d(image), expected), "T2.3: window origin/stride"


def check_core():
    """检查标签、忽略边界、指标与梯度；不依赖学生TODO。"""
    mask = Image.fromarray(np.array([[1, 2, 3]], dtype=np.uint8))
    target, valid = convert_trimap(mask)
    assert target.flatten().tolist() == [1., 0., 0.]
    assert valid.flatten().tolist() == [1., 1., 0.]
    logits = torch.zeros(1, 1, 1, 3, requires_grad=True)
    loss = masked_loss(logits, target[None], valid[None])
    assert abs(loss.item()-np.log(2)) < 1e-6
    loss.backward()
    assert torch.allclose(logits.grad.flatten(), torch.tensor([-.25, .25, 0.]))
    # 有效区域：预测前景3个、真实前景3个、交集2个。
    logits = torch.tensor([[[[1., 1., 1., -1., 100.]]]])
    target = torch.tensor([[[[1., 1., 0., 1., 0.]]]])
    valid = torch.tensor([[[[1., 1., 1., 1., 0.]]]])
    iou, dice = foreground_scores(logits, target, valid)
    assert abs(iou.item()-.5) < 1e-6
    assert abs(dice.item()-2/3) < 1e-6
    empty = torch.zeros_like(target)
    iou, dice = foreground_scores(-torch.ones_like(logits), empty, torch.ones_like(valid))
    assert iou.item() == dice.item() == 1.
    iou, dice = foreground_scores(torch.ones_like(logits), empty, torch.ones_like(valid))
    assert iou.item() == dice.item() == 0.


def check_encoder(improved=False):
    """检查每个阶段的尺寸、有限输出及编码器梯度。

    Args:
        improved (bool): 是否检查改进版。
    """
    encoder = ImprovedEncoder() if improved else PetEncoder()
    images = torch.rand(2, 3, 128, 128)
    features = encoder(images)
    for name, value, shape in zip(["e1", "e2", "z"], features,
                                  [(2,16,64,64), (2,32,32,32), (2,64,16,16)]):
        print(name, tuple(value.shape))
        assert tuple(value.shape) == shape, f"T3: {name} should be {shape}; check Conv/Pool and forward"
        assert torch.isfinite(value).all()
    features[-1].square().mean().backward()
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in encoder.parameters()), "T3: no encoder gradient"


def check_model(name):
    """检查全模型能否输出并完成一次参数更新。

    Args:
        name (str): 模型名称。
    """
    model = build_model(name)
    images = torch.rand(2, 3, 128, 128)
    targets = (images[:, :1] > 0.5).float()
    valid = torch.ones_like(targets)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    before = [p.detach().clone() for p in model.parameters()]
    logits = model(images)
    assert logits.shape == targets.shape, "Output must be [B,1,128,128]"
    loss = masked_loss(logits, targets, valid)
    assert torch.isfinite(loss)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    assert any(not torch.equal(a, b) for a, b in zip(before, model.parameters())), "Parameters did not update"
    model.eval()
    with torch.no_grad():
        assert torch.isfinite(model(images)).all()
    print("output", tuple(logits.shape), "loss", round(loss.item(), 6))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["core", "operators", "encoder", "basic", "improved", "demo"])
    args = parser.parse_args()
    torch.manual_seed(7)
    torch.set_num_threads(2)
    if args.stage == "core":
        check_core()
    elif args.stage == "operators":
        check_operators()
    elif args.stage == "encoder":
        check_encoder()
    else:
        if args.stage in ["basic", "improved"]:
            check_encoder(args.stage == "improved")
        check_model(args.stage)
    print("PASS:", args.stage)
