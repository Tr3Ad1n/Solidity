// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title IStakingPool
 * @notice 质押池接口定义
 */
interface IStakingPool {
    function stake(uint256 amount) external;
    function withdraw(uint256 amount) external;
    function claimReward() external;
    function getStakedBalance(address user) external view returns (uint256);
    function getRewardBalance(address user) external view returns (uint256);
}

