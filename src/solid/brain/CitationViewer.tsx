import "./CitationViewer.css";

interface Citation {
    file: string;
    page: number;
    highlight: string;
}

interface Props {
    citation: Citation;
    onClose: () => void;
}

/**
 * Split-pane PDF citation viewer.
 * Renders the PDF via an <iframe> pointing at the Tauri asset path,
 * and highlights the relevant excerpt in the overlay panel.
 */
export default function CitationViewer(props: Props) {
    // In production, resolve the local file path via Tauri's asset protocol
    const pdfSrc = () => `asset://localhost/${encodeURIComponent(props.citation.file)}#page=${props.citation.page}`;

    return (
        <div class="citation-pane glass anim-fade-in">
            <div class="citation-header">
                <span class="citation-title">{props.citation.file}</span>
                <button id="citation-close" class="citation-close" onClick={props.onClose}>✕</button>
            </div>

            {/* Highlight excerpt */}
            <div class="citation-highlight">
                <span class="citation-page-badge">Page {props.citation.page}</span>
                <blockquote class="highlight-text">"{props.citation.highlight}"</blockquote>
            </div>

            {/* PDF iframe */}
            <iframe
                class="pdf-frame"
                src={pdfSrc()}
                title={`PDF: ${props.citation.file}`}
            />
        </div>
    );
}
