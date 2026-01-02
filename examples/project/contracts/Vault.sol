// 项目示例: Vault合约
pragma solidity ^0.8.0;

import "./Token.sol";

contract Vault {
    Token public token;
    mapping(address => uint256) public deposits;
    address public owner;
    
    constructor(address _token) {
        token = Token(_token);
        owner = msg.sender;
    }
    
    // 漏洞1: 重入攻击风险
    function withdraw(uint256 amount) public {
        require(deposits[msg.sender] >= amount, "Insufficient deposit");
        
        // 外部调用在状态修改之前
        require(token.transfer(msg.sender, amount), "Transfer failed");
        
        // 状态修改在外部调用之后
        deposits[msg.sender] -= amount;
    }
    
    // 漏洞2: 缺少权限控制
    function setToken(address newToken) public {
        token = Token(newToken);
    }
    
    // 漏洞3: 未检查返回值的低级别call
    function emergencyWithdraw(address to) public {
        require(msg.sender == owner, "Only owner");
        uint256 balance = address(this).balance;
        to.call{value: balance}(""); // 未检查返回值
    }
    
    function deposit(uint256 amount) public {
        require(token.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        deposits[msg.sender] += amount;
    }
    
    receive() external payable {
        deposits[msg.sender] += msg.value;
    }
}

