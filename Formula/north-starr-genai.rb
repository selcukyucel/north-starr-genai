class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.14.0.tar.gz"
  sha256 "1359c72ae24fe4910e67d76d31dea55e69de3c36a86fad33400600558b4a2542"
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
