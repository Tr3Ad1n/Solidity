// 示例合约1
pragma solidity ^0.8.0;

contract VulnerableVault {
    mapping(address => uint256) public balances;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    // 重入攻击风险 - 外部调用后修改状态
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // 外部调用在状态修改之前
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        // 状态修改在外部调用之后 - 重入风险！
        balances[msg.sender] -= amount;
    }
    
    // 缺少权限控制 - 任何人都可以调用
    function setOwner(address newOwner) public {
        owner = newOwner;
    }
    
    // 未检查返回值的send
    function emergencyWithdraw() public {
        uint256 balance = balances[msg.sender];
        balances[msg.sender] = 0;
        msg.sender.send(balance); // 未检查返回值
    }
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
}

