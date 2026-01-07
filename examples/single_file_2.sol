// 示例合约2
pragma solidity ^0.8.0;

contract UnsafeContract {
    address public owner;
    mapping(address => bool) public authorized;
    
    constructor() {
        owner = msg.sender;
    }
    
    // 危险的delegatecall
    function executeDelegatecall(address target, bytes memory data) public {
        // 如果target来自用户输入，存在严重风险
        (bool success, ) = target.delegatecall(data);
        require(success, "Delegatecall failed");
    }
    
    // 级别call未检查返回值
    function transferFunds(address to, uint256 amount) public {
        require(authorized[msg.sender], "Not authorized");
        
        // 低级别call，未检查返回值
        to.call{value: amount}("");
    }
    
    // 缺少权限控制的mint函数
    function mint(address to, uint256 amount) public {
        
    }
    
    function authorize(address addr) public {
        require(msg.sender == owner, "Only owner");
        authorized[addr] = true;
    }
}

