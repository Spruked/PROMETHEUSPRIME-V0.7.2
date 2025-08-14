// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract KnowledgeNFT is ERC721URIStorage, Ownable {
    uint256 private _tokenIds;

    struct KnowledgeData {
        address originalCreator;
        string licenseTerms;
        address inheritor;
        bool transferable;
    }

    mapping(uint256 => KnowledgeData) public knowledgeDetails;

    constructor() ERC721("KnowledgeNFT", "KNFT") {}

    function mintKnowledgeNFT(
        address recipient,
        string memory tokenURI,
        string memory licenseTerms,
        address inheritor,
        bool transferable
    ) public onlyOwner returns (uint256) {
        _tokenIds += 1;
        uint256 newItemId = _tokenIds;
        _mint(recipient, newItemId);
        _setTokenURI(newItemId, tokenURI);

        knowledgeDetails[newItemId] = KnowledgeData({
            originalCreator: recipient,
            licenseTerms: licenseTerms,
            inheritor: inheritor,
            transferable: transferable
        });

        return newItemId;
    }

    function getKnowledgeDetails(uint256 tokenId)
        public view returns (KnowledgeData memory)
    {
        require(_exists(tokenId), "Token does not exist");
        return knowledgeDetails[tokenId];
    }

    function transferToInheritor(uint256 tokenId) public {
        KnowledgeData memory data = knowledgeDetails[tokenId];
        require(msg.sender == ownerOf(tokenId), "Only owner can transfer");
        require(data.inheritor != address(0), "No inheritor set");
        require(data.transferable, "Token not marked transferable");

        _transfer(msg.sender, data.inheritor, tokenId);
    }
}