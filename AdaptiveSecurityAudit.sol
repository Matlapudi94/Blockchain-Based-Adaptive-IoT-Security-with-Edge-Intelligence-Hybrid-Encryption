// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract AdaptiveSecurityAudit {
    address public owner;

    struct DecisionRecord {
        string dataId;
        string deviceId;
        string classification;
        string encryptionMode;
        string storageRef;
        string storageKind;
        string timestamp;
        bool exists;
    }

    mapping(bytes32 => DecisionRecord) private decisions;
    mapping(bytes32 => string) private hashes;
    mapping(bytes32 => mapping(string => bool)) private allowedModes;
    mapping(address => mapping(bytes32 => bool)) private permissions;

    event PolicyValidated(bytes32 indexed dataKey, string classification, string encryptionMode);
    event DecisionLogged(bytes32 indexed dataKey, string deviceId, string storageRef);
    event HashLogged(bytes32 indexed dataKey, string hashValue);
    event AccessGranted(address indexed user, bytes32 indexed deviceKey);
    event AccessRevoked(address indexed user, bytes32 indexed deviceKey);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
        _seedPolicies();
    }

    function _seedPolicies() internal {
        allowedModes[_classKey("HIGH")]["AES_FULL"] = true;
        allowedModes[_classKey("HIGH")]["AES_PHE"] = true;
        allowedModes[_classKey("MEDIUM")]["AES_MASK"] = true;
        allowedModes[_classKey("LOW")]["LIGHTWEIGHT"] = true;
        allowedModes[_classKey("LOW")]["NONE"] = true;
    }

    function _classKey(string memory classification) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(classification));
    }

    function setPolicy(string memory classification, string memory encryptionMode, bool allowed) external onlyOwner {
        allowedModes[_classKey(classification)][encryptionMode] = allowed;
    }

    function validateDecision(string memory classification, string memory encryptionMode) external view returns (bool) {
        return allowedModes[_classKey(classification)][encryptionMode];
    }

    function logDecision(
        bytes32 dataKey,
        string memory dataId,
        string memory deviceId,
        string memory classification,
        string memory encryptionMode,
        string memory storageRef,
        string memory storageKind,
        string memory timestamp
    ) external onlyOwner {
        require(allowedModes[_classKey(classification)][encryptionMode], "Policy rejected");
        decisions[dataKey] = DecisionRecord(
            dataId,
            deviceId,
            classification,
            encryptionMode,
            storageRef,
            storageKind,
            timestamp,
            true
        );
        emit PolicyValidated(dataKey, classification, encryptionMode);
        emit DecisionLogged(dataKey, deviceId, storageRef);
    }

    function logHash(bytes32 dataKey, string memory hashValue) external onlyOwner {
        require(decisions[dataKey].exists, "Decision missing");
        hashes[dataKey] = hashValue;
        emit HashLogged(dataKey, hashValue);
    }

    function grantAccess(address user, bytes32 deviceKey) external onlyOwner {
        permissions[user][deviceKey] = true;
        emit AccessGranted(user, deviceKey);
    }

    function revokeAccess(address user, bytes32 deviceKey) external onlyOwner {
        permissions[user][deviceKey] = false;
        emit AccessRevoked(user, deviceKey);
    }

    function authorizeAccess(address user, bytes32 deviceKey) external view returns (bool) {
        return permissions[user][deviceKey];
    }

    function getHash(bytes32 dataKey) external view returns (string memory) {
        return hashes[dataKey];
    }

    function getDecision(bytes32 dataKey)
        external
        view
        returns (
            string memory dataId,
            string memory deviceId,
            string memory classification,
            string memory encryptionMode,
            string memory storageRef,
            string memory storageKind,
            string memory timestamp
        )
    {
        DecisionRecord memory record = decisions[dataKey];
        require(record.exists, "Decision not found");
        return (
            record.dataId,
            record.deviceId,
            record.classification,
            record.encryptionMode,
            record.storageRef,
            record.storageKind,
            record.timestamp
        );
    }
}
