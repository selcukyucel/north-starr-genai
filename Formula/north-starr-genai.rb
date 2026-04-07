class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.14.1.tar.gz"
  sha256 "db9d5d31c87d7793d4ce1830544f33c6e43c352d326b6a4e74e6a81681967d3d"
  license "MIT"

  def install
    bin.install "bin/north-starr-genai"
    (share/"north-starr-genai").install "templates"
    (share/"north-starr-genai").install "skills"
  end

  test do
    system "#{bin}/north-starr-genai", "version"
  end
end
