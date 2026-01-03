// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC20.sol";
import "../interfaces/IStakingPool.sol";

/**
 * @title StakingPool
 * @notice 质押池合约，允许用户质押代币获得奖励
 */
contract StakingPool is IStakingPool {
    ERC20 public stakingToken;
    ERC20 public rewardToken;
    
    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public rewardBalance;
    mapping(address => uint256) public lastUpdateTime;
    
    uint256 public totalStaked;
    uint256 public rewardRate; // 每秒奖励率
    address public owner;
    
    constructor(address _stakingToken, address _rewardToken, uint256 _rewardRate) {
        stakingToken = ERC20(_stakingToken);
        rewardToken = ERC20(_rewardToken);
        rewardRate = _rewardRate;
        owner = msg.sender;
    }
    
    // 漏洞1: 重入攻击风险 - 外部调用在状态修改之前
    function stake(uint256 amount) external override {
        require(amount > 0, "Amount must be greater than 0");
        
        // 外部调用在状态修改之前
        require(stakingToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        // 状态修改在外部调用之后
        if (stakedBalance[msg.sender] > 0) {
            updateReward(msg.sender);
        }
        
        stakedBalance[msg.sender] += amount;
        totalStaked += amount;
        lastUpdateTime[msg.sender] = block.timestamp;
    }
    
    // 漏洞2: 重入攻击风险 - withdraw函数
    function withdraw(uint256 amount) external override {
        require(stakedBalance[msg.sender] >= amount, "Insufficient staked balance");
        
        updateReward(msg.sender);
        
        // 外部调用在状态修改之前
        require(stakingToken.transfer(msg.sender, amount), "Transfer failed");
        
        // 状态修改在外部调用之后
        stakedBalance[msg.sender] -= amount;
        totalStaked -= amount;
    }
    
    // 漏洞3: 缺少权限控制
    function claimReward() external override {
        updateReward(msg.sender);
        uint256 reward = rewardBalance[msg.sender];
        require(reward > 0, "No reward to claim");
        
        rewardBalance[msg.sender] = 0;
        require(rewardToken.transfer(msg.sender, reward), "Transfer failed");
    }
    
    // 漏洞4: 缺少权限控制 - 任何人都可以设置奖励率
    function setRewardRate(uint256 newRate) external {
        rewardRate = newRate;
    }
    
    // 漏洞5: 未检查返回值的低级别call
    function emergencyWithdraw(address to) external {
        require(msg.sender == owner, "Only owner");
        uint256 balance = address(this).balance;
        if (balance > 0) {
            to.call{value: balance}(""); // 未检查返回值
        }
    }
    
    function updateReward(address user) internal {
        if (stakedBalance[user] > 0) {
            uint256 timeElapsed = block.timestamp - lastUpdateTime[user];
            uint256 reward = (stakedBalance[user] * rewardRate * timeElapsed) / 1e18;
            rewardBalance[user] += reward;
        }
        lastUpdateTime[user] = block.timestamp;
    }
    
    function getStakedBalance(address user) external view returns (uint256) {
        return stakedBalance[user];
    }
    
    function getRewardBalance(address user) external view returns (uint256) {
        return rewardBalance[user];
    }
}

