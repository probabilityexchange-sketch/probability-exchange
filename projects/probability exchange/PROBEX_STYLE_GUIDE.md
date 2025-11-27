# probex.markets Style Guide

## Brand Identity

### Logo System
- **Primary Logo**: P(E) symbol with "probex.markets" wordmark
- **Symbol**: Geometric P(E) monogram in brand blue (#00B3FF)
- **Wordmark**: 
  - "probex" in Inter Bold (600 weight)
  - ".markets" in Inter Regular (400 weight)
- **Applications**: Website headers, social profiles, favicon sets

### Color Palette

#### Primary Colors
- **Dark Background**: `#0a0f16` - Main application background
- **Surface Background**: `#141b26` - Cards, panels, secondary backgrounds
- **Brand Blue**: `#00B3FF` - Primary brand color, CTAs, interactive elements
- **Neon Cyan**: `#2EFFFA` - Accent color, highlights, focus states
- **Terminal Gray**: `#7a8a99` - Secondary text, labels, placeholders
- **Pure White**: `#ffffff` - Primary text, content
- **UI Red**: `#FF3366` - Danger states, sell actions, negative indicators

#### Usage Guidelines
- **Dark Background**: Main app background, terminal-style containers
- **Surface Background**: Cards, modals, input fields, navigation
- **Brand Blue**: Primary buttons, links, active states, logo symbol
- **Neon Cyan**: Hover states, focus indicators, success states
- **Terminal Gray**: Secondary text, labels, disabled states
- **Pure White**: Main content text, headers, primary information
- **UI Red**: Error states, sell buttons, warning indicators

### Typography

#### Font Stack
- **Primary Font**: Inter (Google Fonts)
- **Weights**: 400 (Regular), 500 (Medium), 600 (Semi-Bold), 700 (Bold)
- **Applications**:
  - Headers: Inter Bold (700)
  - Subheaders: Inter Semi-Bold (600) 
  - Body Text: Inter Medium (500)
  - Labels: Inter Regular (400)
  - Monospace: Inter (800) for symbols and code

#### Font Sizes
- **Large Headers**: 48px (Main page titles)
- **Medium Headers**: 28px (Section titles)
- **Small Headers**: 24px (Card titles)
- **Body Large**: 16px (Primary content)
- **Body Regular**: 14px (Secondary content)
- **Labels**: 12px (Form labels, metadata)

### UI Components

#### Buttons
1. **Primary Button**
   - Background: `#00B3FF`
   - Text: `#0a0f16`
   - Border Radius: 6px
   - Font: Inter Medium (500)
   - Height: 48px

2. **Secondary Button**
   - Background: Transparent
   - Border: 2px solid `#00B3FF`
   - Text: `#00B3FF`
   - Border Radius: 6px
   - Font: Inter Medium (500)
   - Height: 48px

3. **Tertiary/Ghost Button**
   - Background: Transparent
   - Text: `#7a8a99`
   - Border Radius: 6px
   - Font: Inter Regular (400)
   - Height: 48px

4. **Action Buttons**
   - **Buy YES**: Background `#00B3FF` at 20% opacity
   - **Sell NO**: Background `#FF3366` at 20% opacity
   - Text colors match respective brand colors

#### Input Fields
1. **Standard Input**
   - Background: `#141b26`
   - Border: 2px solid `#2EFFFA` (focus), `#141b26` (default)
   - Text: `#ffffff`
   - Border Radius: 6px
   - Height: 48px
   - Font: Inter Medium (500)

2. **Search Input**
   - Background: `#141b26`
   - Border: 2px solid `#141b26`
   - Text: `#7a8a99` (placeholder)
   - Border Radius: 6px
   - Height: 48px

3. **Dropdown**
   - Background: `#141b26`
   - Border: 1px solid `#7a8a99`
   - Text: `#ffffff`
   - Border Radius: 6px
   - Height: 48px

#### Cards and Panels
- **Background**: `#141b26`
- **Border**: 1px solid `#2EFFFA` at 50% opacity (0.5)
- **Border Radius**: 8px
- **Padding**: 20px standard
- **Shadow**: Subtle, using dark theme principles

#### Navigation
- **Background**: `#0a0f16`
- **Active State**: `#00B3FF` text color
- **Inactive State**: `#7a8a99` text color
- **Hover State**: `#2EFFFA` text color

### Icon System

#### Style
- **Stroke Width**: 2px
- **Stroke Color**: `#7a8a99` (default), `#00B3FF` (active)
- **Line Cap**: Round
- **Line Join**: Round
- **Fill**: None (stroke-based icons)

#### Icon Set
1. **Buy Arrow**: Upward trending line in `#00B3FF`
2. **Sell Arrow**: Downward trending line in `#FF3366`
3. **Charts**: Line graph with ascending trend
4. **Markets**: Horizontal lines of varying lengths
5. **Wallet**: Circular outline with currency symbol

### Layout Principles

#### Grid System
- **Base Unit**: 8px grid system
- **Container Max Width**: 1200px
- **Column Gutter**: 20px
- **Margin**: 30px standard

#### Spacing Scale
- **XS**: 4px
- **SM**: 8px
- **MD**: 16px
- **LG**: 24px
- **XL**: 32px
- **XXL**: 48px

#### Terminal-Style Elements
- **Grid Pattern**: Subtle 60px grid overlay at 8% opacity of `#2EFFFA`
- **Terminal Border**: 2px solid `#141b26` around main containers
- **Code Blocks**: Monospace font, syntax highlighting compatible
- **Command Line**: Terminal-style input with caret cursor

### Application to Dashboard

#### Market Interface Mockup
- **Header**: Logo, navigation menu, wallet balance
- **Market Card**: Dark background with probability chart
- **Probability Chart**: Line graph with `#00B3FF` line, `#2EFFFA` current point
- **Action Panel**: Buy/Sell buttons with amount input
- **Estimation Display**: Payout calculation with `#2EFFFA` highlight

#### Responsive Behavior
- **Desktop**: Full terminal layout with sidebar and main content
- **Tablet**: Collapsed sidebar, maintain terminal aesthetic
- **Mobile**: Stack layout, preserve dark theme and accent colors

### Implementation Notes

#### Streamlit Specific
- Custom CSS injection required for dark theme
- Override default Streamlit color scheme
- Use `st.markdown()` with `unsafe_allow_html=True` for custom components
- Implement custom component styling through CSS classes

#### Accessibility
- Maintain sufficient contrast ratios with dark theme
- Use focus indicators with `#2EFFFA`
- Ensure keyboard navigation support
- Provide alternative text for icon-only buttons

#### Performance
- Use CSS custom properties for theme colors
- Minimize custom font loading
- Optimize SVG icons for web delivery
- Consider CSS-in-JS for dynamic theming

---

*This style guide defines the visual identity for probex.markets prediction markets platform. All design decisions should align with these specifications to maintain consistency across the application.*