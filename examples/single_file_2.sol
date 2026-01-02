// 示例合约2: 包含delegatecall和外部调用风险
pragma solidity ^0.8.0;

contract UnsafeContract {
    address public owner;
    mapping(address => bool) public authorized;
    
    constructor() {
        owner = msg.sender;
    }
    
    // 漏洞1: 危险的delegatecall - 目标可能被用户控制
    function executeDelegatecall(address target, bytes memory data) public {
        // 如果target来自用户输入，存在严重风险
        (bool success, ) = target.delegatecall(data);
        require(success, "Delegatecall failed");
    }
    
    // 漏洞2: 低级别call未检查返回值
    function transferFunds(address to, uint256 amount) public {
        require(authorized[msg.sender], "Not authorized");
        
        // 低级别call，未检查返回值
        to.call{value: amount}("");
    }
    
    // 漏洞3: 缺少权限控制的mint函数
    function mint(address to, uint256 amount) public {
        // 任何人都可以调用，没有onlyOwner修饰符
        // 应该添加: onlyOwner
    }
    
    function authorize(address addr) public {
        require(msg.sender == owner, "Only owner");
        authorized[addr] = true;
    }
}

