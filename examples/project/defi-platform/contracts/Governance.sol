// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC20.sol";

/**
 * @title Governance
 * @notice 治理合约，允许代币持有者投票
 */
contract Governance {
    ERC20 public governanceToken;
    
    struct Proposal {
        string description;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 deadline;
        bool executed;
        address proposer;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(address => uint256) public votingPower;
    
    uint256 public proposalCount;
    uint256 public votingPeriod;
    address public owner;
    
    event ProposalCreated(uint256 indexed proposalId, address indexed proposer, string description);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support);
    event ProposalExecuted(uint256 indexed proposalId);
    
    constructor(address _governanceToken, uint256 _votingPeriod) {
        governanceToken = ERC20(_governanceToken);
        votingPeriod = _votingPeriod;
        owner = msg.sender;
    }
    
    // 漏洞1: 缺少权限控制 - 任何人都可以创建提案
    function createProposal(string memory description) external returns (uint256) {
        proposalCount++;
        proposals[proposalCount] = Proposal({
            description: description,
            votesFor: 0,
            votesAgainst: 0,
            deadline: block.timestamp + votingPeriod,
            executed: false,
            proposer: msg.sender
        });
        
        emit ProposalCreated(proposalCount, msg.sender, description);
        return proposalCount;
    }
    
    // 漏洞2: 重入攻击风险
    function vote(uint256 proposalId, bool support) external {
        require(proposalId > 0 && proposalId <= proposalCount, "Invalid proposal");
        require(!hasVoted[proposalId][msg.sender], "Already voted");
        require(block.timestamp <= proposals[proposalId].deadline, "Voting period ended");
        require(!proposals[proposalId].executed, "Proposal already executed");
        
        uint256 power = governanceToken.balanceOf(msg.sender);
        require(power > 0, "No voting power");
        
        // 外部调用在状态修改之前
        // 这里虽然没有直接的外部调用，但balanceOf是外部调用
        
        // 状态修改
        hasVoted[proposalId][msg.sender] = true;
        if (support) {
            proposals[proposalId].votesFor += power;
        } else {
            proposals[proposalId].votesAgainst += power;
        }
        
        emit VoteCast(proposalId, msg.sender, support);
    }
    
    // 漏洞3: 缺少权限控制 - 任何人都可以执行提案
    function executeProposal(uint256 proposalId) external {
        require(proposalId > 0 && proposalId <= proposalCount, "Invalid proposal");
        require(block.timestamp > proposals[proposalId].deadline, "Voting period not ended");
        require(!proposals[proposalId].executed, "Already executed");
        
        Proposal storage proposal = proposals[proposalId];
        require(proposal.votesFor > proposal.votesAgainst, "Proposal not passed");
        
        proposal.executed = true;
        emit ProposalExecuted(proposalId);
    }
    
    // 漏洞4: 未检查返回值的低级别call
    function emergencyWithdraw(address to) external {
        require(msg.sender == owner, "Only owner");
        uint256 balance = address(this).balance;
        if (balance > 0) {
            to.call{value: balance}(""); // 未检查返回值
        }
    }
    
    function getProposal(uint256 proposalId) external view returns (
        string memory description,
        uint256 votesFor,
        uint256 votesAgainst,
        uint256 deadline,
        bool executed
    ) {
        Proposal memory proposal = proposals[proposalId];
        return (
            proposal.description,
            proposal.votesFor,
            proposal.votesAgainst,
            proposal.deadline,
            proposal.executed
        );
    }
}

