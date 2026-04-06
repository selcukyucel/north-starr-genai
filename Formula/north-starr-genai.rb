class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.12.0.tar.gz"
  sha256 "998e38dc984babd2112e07a00de42f7f8d7e275d0a1905ee8e169e1e8ad5d858"
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
