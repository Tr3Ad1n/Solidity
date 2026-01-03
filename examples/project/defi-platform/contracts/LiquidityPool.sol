// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC20.sol";
import "../libraries/Math.sol";

/**
 * @title LiquidityPool
 * @notice 流动性池合约，实现AMM功能
 */
contract LiquidityPool {
    using Math for uint256;
    
    ERC20 public tokenA;
    ERC20 public tokenB;
    
    uint256 public reserveA;
    uint256 public reserveB;
    
    mapping(address => uint256) public liquidityProviders;
    uint256 public totalLiquidity;
    
    address public owner;
    
    event AddLiquidity(address indexed provider, uint256 amountA, uint256 amountB);
    event RemoveLiquidity(address indexed provider, uint256 amountA, uint256 amountB);
    event Swap(address indexed user, address indexed tokenIn, uint256 amountIn, uint256 amountOut);
    
    constructor(address _tokenA, address _tokenB) {
        tokenA = ERC20(_tokenA);
        tokenB = ERC20(_tokenB);
        owner = msg.sender;
    }
    
    // 漏洞1: 缺少权限控制 - 任何人都可以设置储备量
    function setReserves(uint256 _reserveA, uint256 _reserveB) external {
        reserveA = _reserveA;
        reserveB = _reserveB;
    }
    
    // 漏洞2: 重入攻击风险
    function addLiquidity(uint256 amountA, uint256 amountB) external {
        require(amountA > 0 && amountB > 0, "Amounts must be greater than 0");
        
        // 外部调用在状态修改之前
        require(tokenA.transferFrom(msg.sender, address(this), amountA), "Transfer A failed");
        require(tokenB.transferFrom(msg.sender, address(this), amountB), "Transfer B failed");
        
        // 状态修改在外部调用之后
        reserveA += amountA;
        reserveB += amountB;
        
        uint256 liquidity = Math.sqrt(amountA * amountB);
        liquidityProviders[msg.sender] += liquidity;
        totalLiquidity += liquidity;
        
        emit AddLiquidity(msg.sender, amountA, amountB);
    }
    
    // 漏洞3: 重入攻击风险
    function removeLiquidity(uint256 liquidity) external {
        require(liquidityProviders[msg.sender] >= liquidity, "Insufficient liquidity");
        
        uint256 amountA = (reserveA * liquidity) / totalLiquidity;
        uint256 amountB = (reserveB * liquidity) / totalLiquidity;
        
        // 外部调用在状态修改之前
        require(tokenA.transfer(msg.sender, amountA), "Transfer A failed");
        require(tokenB.transfer(msg.sender, amountB), "Transfer B failed");
        
        // 状态修改在外部调用之后
        liquidityProviders[msg.sender] -= liquidity;
        totalLiquidity -= liquidity;
        reserveA -= amountA;
        reserveB -= amountB;
        
        emit RemoveLiquidity(msg.sender, amountA, amountB);
    }
    
    // 漏洞4: 未检查返回值的低级别call
    function swap(address tokenIn, uint256 amountIn) external returns (uint256) {
        require(tokenIn == address(tokenA) || tokenIn == address(tokenB), "Invalid token");
        
        ERC20 token = ERC20(tokenIn);
        require(token.transferFrom(msg.sender, address(this), amountIn), "Transfer failed");
        
        uint256 amountOut;
        if (tokenIn == address(tokenA)) {
            amountOut = (amountIn * reserveB) / reserveA;
            reserveA += amountIn;
            reserveB -= amountOut;
            require(tokenB.transfer(msg.sender, amountOut), "Transfer failed");
        } else {
            amountOut = (amountIn * reserveA) / reserveB;
            reserveB += amountIn;
            reserveA -= amountOut;
            require(tokenA.transfer(msg.sender, amountOut), "Transfer failed");
        }
        
        emit Swap(msg.sender, tokenIn, amountIn, amountOut);
        return amountOut;
    }
    
    // 漏洞5: 危险的delegatecall
    function executeDelegatecall(address target, bytes calldata data) external {
        require(msg.sender == owner, "Only owner");
        (bool success, ) = target.delegatecall(data);
        // 未检查success
    }
}

