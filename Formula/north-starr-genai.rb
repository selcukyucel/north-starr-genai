class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.12.0.tar.gz"
  sha256 "9f274664d24baa30adc8f564303d6fdbcde81c4d47d4805240a9e48ac0f8eac6"
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
