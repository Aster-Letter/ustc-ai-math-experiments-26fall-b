"""学生训练入口：python train.py --output outputs/run-01。"""
import student
from checks import run_checks
from engine import parser, train

if __name__ == "__main__":
    args = parser().parse_args()
    run_checks(student)
    train(student, args)
