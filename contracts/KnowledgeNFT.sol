// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract KnowledgeNFT is ERC721URIStorage, Ownable {
    uint256 private _tokenIds;

    constructor() ERC721("KnowledgeNFT", "KNFT") {}

    function mintKnowledgeNFT(address recipient, string memory tokenURI)
        public onlyOwner
        returns (uint256)
    {
        _tokenIds += 1;
        uint256 newItemId = _tokenIds;
        _mint(recipient, newItemId);
        _setTokenURI(newItemId, tokenURI);
        return newItemId;
    }

    function currentTokenId() public view returns (uint256) {
        return _tokenIds;
    }
}