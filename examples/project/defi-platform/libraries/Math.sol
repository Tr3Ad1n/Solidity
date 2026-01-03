// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Math Library
 * @notice 数学工具库
 */
library Math {
    /**
     * @notice 计算平方根（简化版）
     * @param x 输入值
     * @return 平方根结果
     */
    function sqrt(uint256 x) internal pure returns (uint256) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        uint256 y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
        return y;
    }
    
    /**
     * @notice 计算最小值
     */
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
    
    /**
     * @notice 计算最大值
     */
    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }
}

