class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.12.0.tar.gz"
  sha256 "5d00c44a6fcbff6d1fc5199f5ca098d3ed78d04023d0541c295f07747c8e2832"
  license "MIT"

  def install
    bin.install "bin/north-starr-genai"
    (share/"north-starr-genai").install "templates"
    (share/"north-starr-genai").install "skills"
  end

  test do
    assert_match "north-starr-genai v", shell_output("#{bin}/north-starr-genai version")
  end
end
